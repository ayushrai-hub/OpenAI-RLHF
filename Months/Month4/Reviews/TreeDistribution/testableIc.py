import numpyro
import numpyro.distributions as dist
from numpyro.distributions import Distribution, constraints
import jax
import jax.numpy as jnp
from jax import lax

class TreeDistribution(Distribution):
    support = constraints.integer_interval(0, 2)

    def __init__(self, probabilities: jnp.ndarray, max_depth: int, validate_args: bool = None) -> None:
        self.probabilities = probabilities
        self.max_depth = max_depth
        batch_shape = ()
        event_shape = (max_depth,)
        super(TreeDistribution, self).__init__(batch_shape, event_shape, validate_args)

    def sample(self, key: jax.random.PRNGKey, sample_shape: tuple = ()) -> jnp.ndarray:
        shape = sample_shape + (self.max_depth,)
        logits = jnp.log(self.probabilities)
        decisions = jax.random.categorical(key, logits=logits, shape=shape)
        return decisions

    def log_prob(self, value: jnp.ndarray) -> jnp.ndarray:
        if value.shape[-1] != self.max_depth:
            raise ValueError(f"Expected last dimension of value to be {self.max_depth}, got {value.shape[-1]}")
        decision_probs = self.probabilities[value]
        log_probs = jnp.log(decision_probs)
        return jnp.sum(log_probs, axis=-1)

def scan_body(carry: tuple, _: None) -> tuple:
    key, probabilities = carry
    key, subkey = jax.random.split(key)
    decision = numpyro.sample('decision', dist.Categorical(probabilities))
    return (key, probabilities), decision

def model() -> None:
    x = 0.3
    y = 0.5
    z = 0.2
    probabilities = jnp.array([x, y, z])
    max_depth = 5
    keys = jax.random.split(numpyro.sample('rng_key', dist.PRNGIdentity()), max_depth)
    _, decisions = lax.scan(scan_body, (keys[0], probabilities), None, length=max_depth)
