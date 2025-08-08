# Let's count the columns in the INSERT statement from the code:

insert_columns = [
    "employee_id", "technical_unit_id", "project_id", "service_id",
    "estimated_hours", "actual_hours", "hourly_rate", "total_cost", 
    "booking_status", "booking_date", "start_date", "end_date", "notes",
    "created_by", "approved_by", "created_at", "updated_at",
    "cost_center", "ghrs_id", "employee_name", "dept_description",
    "work_location", "business_unit", "tipo", "tipo_description", "sap_tipo",
    "saabu_rate_eur", "saabu_rate_usd", "local_agency_rate_usd", "unit_rate_usd",
    "monthly_hours", "annual_hours", "workload_2025_planned", "workload_2025_actual",
    "remark", "project_name", "item", "technical_unit_name", "activities_name",
    "booking_hours", "booking_cost_forecast", "booking_period",
    "booking_hours_accepted", "booking_period_accepted", "booking_hours_extra"
]

print(f"INSERT columns count: {len(insert_columns)}")
print("\nINSERT columns:")
for i, col in enumerate(insert_columns):
    print(f"{i+1:2d}. {col}")

# Expected VALUES count
values_params = [
    "employee_id", "tech_unit_id", "project_id", "service_id",
    "total_estimated", "start_date", "end_date", "service_notes",
    "cost_center", "ghrs_id", "emp_name", "dept_description",
    "work_location", "business_unit", "tipo", "tipo_description", "sap_tipo",
    "saabu_rate_eur", "saabu_rate_usd", "local_agency_rate_usd", "unit_rate_usd",
    "monthly_hours", "annual_hours", "workload_2025_planned", "workload_2025_actual",
    "remark", "project_name_val", "tu_name_val", "activity_name_val"
]

print(f"\nVALUES parameters count: {len(values_params)}")
print("\nVALUES parameters:")
for i, param in enumerate(values_params):
    print(f"{i+1:2d}. {param}")

print(f"\nDifference: {len(insert_columns) - len(values_params)} columns")
