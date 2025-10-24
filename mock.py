HEALTH_DATA = {
    "health_metrics": {
        "height_cm": 175,
        "weight_kg": 78,        # tăng cân → có thể thừa cân
        "age": 28,
        "gender": "male",
        "bmi": 25.5,            # vượt mức bình thường (thừa cân nhẹ)
        "bmr": 1750,            # tăng nhẹ do khối lượng cơ thể lớn hơn
        "tdee": 2300            # giảm so với trước → ít vận động hơn
    },
    "blood_test": {
        "glucose_mg_dL": 110,   # cao hơn mức bình thường → nguy cơ tiền tiểu đường
        "cholesterol_total_mg_dL": 220,  # cao → rối loạn mỡ máu
        "hdl_mg_dL": 38,        # thấp → không tốt
        "ldl_mg_dL": 145,       # cao → nguy cơ tim mạch
        "triglycerides_mg_dL": 180,  # cao → rối loạn lipid
        "vitamin_d_ng_mL": 18   # thiếu hụt vitamin D
    },
    "urine_test": {
        "ph": 5.5,              # hơi acid → có thể do chế độ ăn hoặc stress
        "protein": "trace",     # có vết protein → dấu hiệu cảnh báo thận
        "glucose": "trace"      # có vết glucose → cảnh báo rối loạn đường huyết
    }
}

health_improvement_options = {
    "health_improvement_options": [
        {
            "id": "gain_weight",
            "label": "Tăng cân",
            "description": "Muốn tăng cân một cách lành mạnh, cải thiện khối lượng cơ thể."
        },
        {
            "id": "lose_weight",
            "label": "Giảm cân",
            "description": "Muốn giảm cân, giảm mỡ thừa và cải thiện vóc dáng."
        },
        {
            "id": "build_muscle",
            "label": "Tăng cơ",
            "description": "Muốn tăng khối lượng cơ bắp, cải thiện sức mạnh và thể hình."
        },
        {
            "id": "improve_health_metrics",
            "label": "Cải thiện chỉ số sức khoẻ",
            "description": "Muốn cải thiện các chỉ số như đường huyết, cholesterol, vitamin D, v.v."
        }
    ]
}

USER_OPTIONS = {
    "user_options": [
        {
            "id": "improve_health_metrics",
            "label": "Cải thiện chỉ số sức khoẻ",
            "description": "Muốn cải thiện các chỉ số như đường huyết, cholesterol, vitamin D, v.v."
        }
    ]
}