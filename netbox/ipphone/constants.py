
# EXTENSION statuses
EXTENSION_STATUS_ACTIVE = 1
EXTENSION_STATUS_INACTIVE = 2
EXTENSION_STATUS_CHOICES = (
    (EXTENSION_STATUS_ACTIVE, 'Active'),
    (EXTENSION_STATUS_INACTIVE, 'Inactive')
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