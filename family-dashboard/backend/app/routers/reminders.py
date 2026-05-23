from .. import models, schemas
from ._generic import make_router

router = make_router(
    "/reminders", "reminders",
    models.Reminder,
    schemas.ReminderCreate,
    schemas.ReminderRead,
    schemas.ReminderUpdate,
)
