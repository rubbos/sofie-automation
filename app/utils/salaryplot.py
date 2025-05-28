import matplotlib.pyplot as plt
import calculations
import numpy as np

monthly_salaries = np.linspace(1000, 6000, 200)

percentages_age_30plus = [calculations.salary_percentage(s, 30) for s in monthly_salaries]
percentages_under_30 = [calculations.salary_percentage(s, 25) for s in monthly_salaries]

plt.figure(figsize=(10, 6))
plt.plot(monthly_salaries, percentages_age_30plus, label="Age ≥ 30")
plt.plot(monthly_salaries, percentages_under_30, label="Age < 30")
plt.xlabel("Monthly Salary (€)")
plt.ylabel("Applicable Percentage (%)")
plt.legend()
plt.grid(True)
plt.xlim(2500, 5500)  
plt.tight_layout()
plt.show()
plt.savefig('salaryplot.png')