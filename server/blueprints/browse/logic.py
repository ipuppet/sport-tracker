from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from server.models import (
    db,
    Exercise,
    BodyMeasurement,
    BodyMeasurementType,
    Achievement,
    CalorieIntake,
)
from server.utils.constants import ExerciseType, EXERCISE_METRICS, ACHIEVEMENTS


def get_exercise_types() -> dict:
    return {e.name: str(e) for e in ExerciseType}


def get_exercises_metrics() -> dict:
    return {e.name: EXERCISE_METRICS[e] for e in ExerciseType}


def add_exercise_data(
    exercise_type: ExerciseType,
    metrics,
    created_at,
) -> Achievement | None:
    try:
        new_exercise = Exercise(
            user_id=current_user.id,
            type=exercise_type,
            metrics=metrics,
            created_at=created_at,
        )
        db.session.add(new_exercise)
        # Check achievements
        exercises = current_user.exercises.filter_by(type=exercise_type).all()
        total = sum(
            float(ex.metrics.get(EXERCISE_METRICS[exercise_type][0], 0))
            for ex in exercises
        )
        achievements = current_user.achievements.filter_by(
            exercise_type=exercise_type
        ).all()
        new_achievement = None
        for milestone in ACHIEVEMENTS[exercise_type]:
            if total >= milestone and not any(
                a.milestone == milestone for a in achievements
            ):
                new_achievement = Achievement(
                    user_id=current_user.id,
                    exercise_type=exercise_type,
                    milestone=milestone,
                )
                db.session.add(new_achievement)
        db.session.commit()
        return new_achievement
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding exercise data: {str(e)}")


def get_body_measurement_types() -> dict:
    return {e.name: str(e) for e in BodyMeasurementType}


def add_body_measurement_data(
    bm_type: BodyMeasurementType,
    value,
    created_at,
):
    try:
        new_body_measurement = BodyMeasurement(
            user_id=current_user.id,
            type=bm_type,
            value=value,
            created_at=created_at,
        )
        db.session.add(new_body_measurement)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding body measurement data: {str(e)}")


def add_calorie_intake_data(calories, description, created_at):
    try:
        new_calorie_intake = CalorieIntake(
            user_id=current_user.id,
            calories=calories,
            description=description,
            created_at=created_at,
        )
        db.session.add(new_calorie_intake)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding calorie intake data: {str(e)}")
