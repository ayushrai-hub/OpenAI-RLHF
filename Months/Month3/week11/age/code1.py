# compute the employed numbers and per sector numbers

# Given values:
lf_2012 = 671043786
ur_2012 = 7.71230864998509  # unemployment rate in %
lf_2022 = 712310322
ur_2022 = 4.47915987611736

# Employed = Labor force * (1 - UR/100)
emp_2012 = lf_2012 * (1 - ur_2012/100.0)
emp_2022 = lf_2022 * (1 - ur_2022/100.0)

# Sector percentages for 2012 and 2022
# percentages in %, convert to fraction to multiply
agri_2012 = 4.2195801167456
ind_2012  = 23.7756871492213
serv_2012 = 72.0047329076567

agri_2022 = 3.26186835410967
ind_2022  = 22.6229402469026
serv_2022 = 74.1151925928055

# compute employment per sector
def sector_employment(total_emp, pct):
    return total_emp * pct / 100.0

# 2012
emp_agri_2012 = sector_employment(emp_2012, agri_2012)
emp_ind_2012 = sector_employment(emp_2012, ind_2012)
emp_serv_2012 = sector_employment(emp_2012, serv_2012)

# 2022
emp_agri_2022 = sector_employment(emp_2022, agri_2022)
emp_ind_2022 = sector_employment(emp_2022, ind_2022)
emp_serv_2022 = sector_employment(emp_2022, serv_2022)

# net changes
delta_agri = emp_agri_2022 - emp_agri_2012
delta_ind = emp_ind_2022 - emp_ind_2012
delta_serv = emp_serv_2022 - emp_serv_2012

# Print results
print("Employed total 2012: {:.0f}".format(emp_2012))
print("Employed total 2022: {:.0f}".format(emp_2022))

print("\nEmployment per sector 2012 (million):")
print("Agriculture: {:.0f}".format(emp_agri_2012))
print("Industry: {:.0f}".format(emp_ind_2012))
print("Services: {:.0f}".format(emp_serv_2012))

print("\nEmployment per sector 2022 (million):")
print("Agriculture: {:.0f}".format(emp_agri_2022))
print("Industry: {:.0f}".format(emp_ind_2022))
print("Services: {:.0f}".format(emp_serv_2022))

print("\nNet change 2012→2022 (million):")
print("Agriculture: {:+.0f}".format(delta_agri))
print("Industry: {:+.0f}".format(delta_ind))
print("Services: {:+.0f}".format(delta_serv))

