print("How many kilometers did you cycle today?")
kms = float(input())
miles=kms/1.60934
miles=round(miles,2)
print(f"Your {kms}km ride is equivalent to {miles}mi")
