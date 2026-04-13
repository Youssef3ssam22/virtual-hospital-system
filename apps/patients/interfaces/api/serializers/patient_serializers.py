"""DRF serializers for patients endpoints."""

from rest_framework import serializers


class PatientRegisterSerializer(serializers.Serializer):
    mrn = serializers.CharField(max_length=32)
    national_id = serializers.CharField(max_length=32)
    full_name = serializers.CharField(max_length=255)
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=["MALE", "FEMALE"])
    blood_type = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    )
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)


class PatientUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False, max_length=255)
    gender = serializers.ChoiceField(required=False, choices=["MALE", "FEMALE"])
    blood_type = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    )
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)


class PatientResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    mrn = serializers.CharField()
    national_id = serializers.CharField()
    full_name = serializers.CharField()
    date_of_birth = serializers.DateField()
    gender = serializers.CharField()
    blood_type = serializers.CharField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    is_active = serializers.BooleanField()


class PatientAllergySerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    patient_id = serializers.CharField(required=False)
    allergy_code = serializers.CharField(max_length=50)
    allergy_name = serializers.CharField(max_length=255)
    severity = serializers.ChoiceField(choices=["MILD", "MODERATE", "SEVERE"])
    recorded_by = serializers.CharField(max_length=100)
    is_active = serializers.BooleanField(required=False)
