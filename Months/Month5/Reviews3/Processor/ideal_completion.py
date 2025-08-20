#ideal_completion.py

class IntegratedProcessor(object):
    """
    PURPOSE: Extends from distributor.
    PARAMETERS: phi_init = initial density setup, None = random choice, 'env_default' = ENV.start
                mass = consider particle momentum, roughly equals the #previous states avoided
                            # TODO revamp as self-motion indicator
                prevent_dwell = True, avoid sampling present state (i.e. enforce jump, -> embedded discrete-time chain)
                diagnostics = computes coverage efficiency/MSD etc. for sample paths
    """
    def __init__(self, PROP, phi_init='env_default', mass=1, prevent_dwell=True, name='PROCESSOR', out_dir='processing', scenario=False, **kwargs):
        self.PROP = PROP
        self.scenario = scenario  # Marker for scenario features
        if phi_init == 'env_default':
            self.phi_init = handle_phi(self.ENV.start, self.n_state)
        else:
            self.phi_init = handle_phi(phi_init, self.n_state)
        self.prevent_dwell = prevent_dwell
        self.mass = mass
        self.name = name
        self.out_dir = out_dir
        self.series_sampled = False
        if hasattr(self.ENV, 'R') or hasattr(self.ENV, 'R_state'):
            self.no_reward_func = False # sampling functions will collect rewards
        else:
            self.no_reward_func = True # sampling functions will omit rewards
        for key, value in kwargs.items():
            setattr(self, key, value)

        np.random.seed()
        assert self.phi_init.size == self.PROP.n_state, 'Starting state density dimensions mismatch.'

    @property
    def gamma(self):
        return self.PROP.gamma

    @property
    def n_dim(self):
        return self.PROP.n_dim

    @property
    def n_state(self):
        return self.PROP.n_state

    @property
    def index_states(self):
        return self.PROP.states

    @property
    def env_array(self):
        return self.GEN.ENV.env_array

    @property
    def GEN(self):
        return self.PROP.GEN

    @property
    def ENV(self):
        return self.PROP.GEN.ENV

    @ENV.setter
    def ENV(self, value):
        self.PROP.GEN.ENV = value

    @debug_time
    @jit(nopython=config.jit_nopython, parallel=config.jit_nopython, cache=config.jit_cache)
    def progress(self, n_step=1, phi_init=None, overlook_imag=True):
        if phi_init is None:
            phi_init = self.phi_init
        self._validate_state_density(phi_state=phi_init)
        for i in range(n_step):
            phi_hi = np.dot(phi_init, self.PROP.etO)
            if not np.all(np.isreal(phi_hi)):
                if overlook_imag:
                    print('PROCESSOR: density transitioned to complex')
                    phi_hi = phi_hi.real
                else:
                    raise ValueError('PROCESSOR: complex transition density')
            phi_hi = normalize_density(phi_hi, gamma=self.gamma, type='l1')  # L1 normalize
            phi_init = phi_hi
        self._validate_state_density(phi_state=phi_init)
        return phi_init

    @debug_time
    def _validate_state_density(self, phi_state, decimal_accuracy=config.decimal_accuracy):
        assert (phi_state >= 0).all(), 'Negative range in state density.'
        if np.allclose(phi_state.sum(), 1):
            return phi_state / phi_state.sum()
        else:
            raise ValueError('PROCESSOR: State density sum equals %.8f (!= 1).' % phi_state.sum())

    @debug_time
    def _state_sample(self, phi_state, past_states=None):
        if (self.prevent_dwell and self.mass != 0.) and past_states is not None:
            mass = np.floor(self.mass).astype('int')
            states = past_states
            except_states = states[~np.isnan(states)].astype('int')
            except_states = except_states[-np.min([mass, len(except_states)]):]  # "state memory"
            phi_state[except_states] = 0.
        phi_state = phi_state / phi_state.sum()
        return sample_entity(phi_state)

    @debug_time
    def _reward_sample(self, current_state, prior_state=None):
        if prior_state is None:
            reward = self.ENV.R_state[current_state]
        else:
            reward = self.ENV.R[prior_state, current_state]
        return reward

    @info_time
    @jit(nopython=config.jit_nopython, parallel=config.jit_nopython, cache=config.jit_cache)
    def generate_series(self, n_step=100, n_samp=50, phi_start=None, quick_store=True):
        self.series_generated = True
        self.quick_store = quick_store
        if phi_start is None:
            phi_start = self.phi_init
        phi_start = handle_phi(phi_start, self.n_state)
        seq_steps_total = n_step + 1  # account for initial state
        self.n_step = n_step
        self.n_samp = n_samp
        self.seq_steps_total = seq_steps_total
        self.step_index = np.arange(0, seq_steps_total, 1)
        self.samp_index = np.arange(0, n_samp, 1)
        self.sample_times = self.step_index * (1 / self.PROP.tau)
        self.slice_index = pd.IndexSlice

        if config.verbose:
            iterator = tqdm(range(n_samp), desc='GENERATING')
        else:
            iterator = range(n_samp)

        state_series = np.zeros((n_samp, seq_steps_total))
        phi_vals = np.zeros((n_samp, seq_steps_total, self.n_state))
        gained_rewards = np.zeros((n_samp, seq_steps_total))
        log_pvals = torch.zeros((n_samp, seq_steps_total))

        for ns in iterator:
            current_state = self._state_sample(phi_start)
            state_series[ns, 0] = current_state
            phi_vals[ns, 0, :] = phi_start  # consider phi_hi convention at step 0
            log_pvals[ns, 0] = Categorical(torch.tensor(phi_start)).log_prob(torch.tensor(current_state)).item()

            if not self.no_reward_func:
                gained_rewards[ns, 0] = self._reward_sample(current_state)

            phi_interim = handle_phi(current_state, self.n_state)  # sampled state as succeeding step prior
            for n in range(1, seq_steps_total):
                phi_hi = self.progress(n_step=1, phi_start=phi_interim)
                current_state = self._state_sample(phi_hi, past_states=np.array(state_series[ns, :n]))
                state_series[ns, n] = current_state
                phi_vals[ns, n, :] = phi_hi
                log_pvals[ns, n] = Categorical(torch.tensor(phi_hi)).log_prob(torch.tensor(current_state)).item()
                if not self.no_reward_func:
                    gained_rewards[ns, n] = self._reward_sample(current_state)
                phi_interim = handle_phi(current_state, self.n_state)

        if quick_store:
            self.state_series = state_series.astype('int')
            self.phi_vals = phi_vals
            self.gained_rewards = gained_rewards
            self.log_pvals = log_pvals
        else:
            self.scalar_output.loc[self.slice_index[:, :], 'state'] = state_series.flatten()
            self.vector_output.loc[self.slice_index[:, :, :], 'phi_hi'] = phi_vals.flatten()
            self.scalar_output.loc[self.slice_index[:, :], 'reward'] = gained_rewards.flatten()
            self.scalar_output.loc[self.slice_index[:, :], 'log_pval'] = log_pvals.flatten()


    def plot_path(self, samp=0):
        positions = np.array(self._retrieve_state(samp=samp, step=None, coords=True))
        positions = pd.DataFrame(positions, columns=["x", "y"])
        return (
            so.Plot(self.ENV.detail_state, x="x", y="y", color="color")
            .add(so.Dot())
            .scale(
                color=so.Nominal(),
                x=so.Temporal()
            )
            .add(so.Line(positions, color="black"))
        )

    def calculate_cf(self, axis=None, dist_occ=0, zero_pos=False):
        if self.scenario:
            sampled_state = self.ENV.states[self.state_series]
            sampled_state[:, :, 0] = self.ENV.semantic_mds[sampled_state[:, :, 0].astype(int)]
            sampled_state[:, :, 2] = self.ENV.spatial_mds[sampled_state[:, :, 2].astype(int)]
            sampled_state = sampled_state[:, :, 0:3]
            self.acf_mean, self.acf_sem = estimate_scenario_acf_v2(sampled_state, axis=axis)
        else:
            sampled_state = self._retrieve_state(samp=None, step=None, coords=False)
            if zero_pos:
                self.acf_mean, self.acf_sem = estimate_occ_acf_zero(sampled_state.T, d=dist_occ)
            else:
                self.acf_mean, self.acf_sem = estimate_occ_acf(sampled_state.T, d=dist_occ)

