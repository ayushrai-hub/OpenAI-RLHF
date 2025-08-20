def generate_turbine_dropdowns(self):
    # Erase any dropdowns already created
    for widget in self.turbine_frame.winfo_children():
        widget.destroy()

    self.turbine_dropdowns = []
    try:
        num_units = int(self.num_units.get())
    except ValueError:
        messagebox.showerror("Error", "You must enter a valid count for units.")
        return

    for i in range(num_units):
        label = ttk.Label(self.turbine_frame, text=f"Turbine {i + 1}:")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        turbine_var = tk.StringVar()
        turbine_dropdown = ttk.Combobox(self.turbine_frame, textvariable=turbine_var, state="readonly", width=30)
        turbine_dropdown['values'] = [turbine['name'] for turbine in turbines]
        turbine_dropdown.grid(row=i, column=1, padx=10, pady=5, sticky="we")
        self.turbine_dropdowns.append(turbine_dropdown)

def calculate(self):
    self.results_text.config(state="normal")
    self.results_text.delete(1.0, tk.END)

    try:
        min_power = float(self.min_power.get())
        max_power = float(self.max_power.get())
        num_units = int(self.num_units.get())
        capacity_utilization = float(self.capacity_utilization.get())
        is_urban = self.location_var.get() == "Urban"
        chosen_fuel = self.fuel_var.get()
        chosen_turbines = [dropdown.get() for dropdown in self.turbine_dropdowns]
    except ValueError:
        messagebox.showerror("Error", "Please provide valid numeric values for power range, units, and utilization.")
        return

    if not chosen_fuel:
        messagebox.showerror("Error", "Select a fuel type.")
        return

    if not all(chosen_turbines):
        messagebox.showerror("Error", "Select a turbine for each unit.")
        return

    if not (min_power <= max_power):
        messagebox.showerror("Error", "Minimum power must be less than or equal to maximum.")
        return

    self.results_text.insert(tk.END, f"Evaluating cost per kWh for turbines in range {min_power} MW to {max_power} MW\n\n")

    # Go through each turbine and each fuel
    for turbine_name, fuel_name in product([turbine['name'] for turbine in turbines], fuels.keys()):
        turbine = next(t for t in turbines if t["name"] == turbine_name)
        fuel = fuels[fuel_name]

        # Estimate the power plant capacity based on the units and turbine power
        plant_capacity_mw = min_power + (max_power - min_power) * (turbine["power"] / max(t["power"] for t in turbines))

        # Compute the mass flow rate of fuel
        mass_flow_rate = (turbine["heat_rate"] * plant_capacity_mw * 1000) / (2 * fuel["calorific_value"])
        
        # Compute fuel cost per kWh
        fuel_cost_per_kwh = (mass_flow_rate / 3600) * fuel["cost_per_kg"]

        self.results_text.insert(tk.END, f"Turbine: {turbine['name']} | Fuel: {fuel_name} | Capacity: {plant_capacity_mw:.2f} MW | Fuel Cost per kWh: ${fuel_cost_per_kwh:.4f}\n")

    self.results_text.config(state="disabled")