from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

User = get_user_model()

logger = logging.getLogger(__name__)

"""
A signal is Django's way of saying — "when X happens anywhere in the app, automatically run Y" 
— without the code that causes X needing to know anything about Y.

post_save — a built-in signal that Django fires automatically every time any model's .save() method finishes successfully
receiver — a decorator that connects your function to listen for that signal
sender — the model class that triggered the signal (in this case, always User, since we filtered with sender=User)
instance — the actual object instance that was just saved (a specific User record)
created — a boolean: True if this was a brand new record (INSERT), False if it was an update to an existing record (UPDATE)
**kwargs — Django always passes extra keyword arguments to signal receivers (like using, raw, update_fields) — you don't need them here, but your function signature must accept them or Django will throw an error when calling**kwargs — Django always passes extra keyword arguments to signal receivers (like using, raw, update_fields) — you don't need them here, but your function signature must accept them or Django will throw an error when calling

pre_save     # fires BEFORE the record is saved
post_save    # fires AFTER the record is saved (what you're using)
pre_delete   # fires BEFORE a record is deleted
post_delete  # fires AFTER a record is deleted
m2m_changed  # fires when a ManyToMany relationship changes

"""


class UserProfileSignalHandler:
    """
    Handles creating the correct profile (Patient/Consultant)
    whenever a new User is created.
    """

    @staticmethod
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance: User, created, **kwargs):
        if created:
            try:
                if instance.role and instance.role.code == "patient":
                    from base.services.services import PatientProfileService

                    PatientProfileService().create(user=instance)
                    logger.info(f"Created patient profile for user {instance.id}")

                elif instance.role == "consultant":
                    from base.services.services import ConsultantProfileService

                    ConsultantProfileService().create(user=instance)
                    logger.info(
                        f"Consultant user created {instance.id} - profile will be created when speciality is assigned"
                    )

            except Exception as ex:
                logger.error(
                    f"Error creating profile for user {instance.id} : {str(ex)}"
                )
