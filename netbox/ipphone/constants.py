
# PHONE statuses
PHONE_STATUS_ACTIVE = 1
PHONE_STATUS_INACTIVE = 2
PHONE_STATUS_CHOICES = (
    (PHONE_STATUS_ACTIVE, 'Active'),
    (PHONE_STATUS_INACTIVE, 'Inactive')
)

# Bootstrap CSS classes
STATUS_CHOICE_CLASSES = {
    0: 'default',
    1: 'primary',
    2: 'info',
    3: 'danger',
    4: 'warning',
    5: 'success',
}