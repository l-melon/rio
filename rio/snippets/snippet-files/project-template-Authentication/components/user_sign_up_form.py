import rio

# <additional-imports>
from .. import data_models, persistence

# </additional-imports>


# <component>
class UserSignUpForm(rio.Component):
    """
    Provides interface for users to sign up for a new account.

    It includes fields for username and password, handles user creation, and
    displays error messages if the sign-up process fails.
    """

    # This will be set to `True` when the sign-up popup is open
    popup_open: bool

    # These fields will be bound to the input fields in the form. This allows us
    # to easily access the values entered by the user.
    username_sign_up: str = ""
    password_sign_up: str = ""
    password_sign_up_repeat: str = ""

    # This field will be used to display an error message if the sign-up process
    # fails.
    error_message: str = ""

    # These fields will be updated to reflect the validity of the username and
    # passwords entered by the user. If they are invalid, we will display an
    # error message to the user.
    username_valid: bool = True
    passwords_valid: bool = True

    async def on_sign_up(self) -> None:
        """
        Handles the sign-up process when the user submits the sign-up form.

        It will check if the user already exists and if the passwords match. If
        the user does not exist and the passwords match, a new user will be
        created and stored in the database.
        """
        # Get the persistence instance. It was attached to the session earlier,
        # so we can easily access it from anywhere.
        pers = self.session[persistence.Persistence]

        # Check if username and passwords are empty
        if (
            not self.username_sign_up
            or not self.password_sign_up
            or not self.password_sign_up_repeat
        ):
            self.error_message = "Please fill in all fields"
            self.passwords_valid = False
            self.username_valid = False
            return

        # Check if the passwords match
        if self.password_sign_up != self.password_sign_up_repeat:
            self.error_message = "Passwords do not match"
            self.passwords_valid = False
            self.username_valid = True
            return

        # Check if this username is available
        try:
            await pers.get_user_by_username(username=self.username_sign_up)
        except KeyError:
            pass
        else:
            self.error_message = "User already exists"
            self.username_valid = False
            self.passwords_valid = True
            return

        # Create a new user
        user_info = data_models.AppUser.new_with_defaults(
            username=self.username_sign_up,
            password=self.password_sign_up,
        )

        # Store the user in the database
        await pers.add_user(user_info)

        # Registration is complete - close the popup
        self.popup_open = False

    def on_cancel(self) -> None:
        """
        Closes the sign-up popup when the user clicks the cancel button.

        It also resets all fields to their default values.
        """
        # Set all fields to default values
        self.username_valid: bool = True
        self.passwords_valid: bool = True
        self.username_sign_up: str = ""
        self.password_sign_up: str = ""
        self.password_sign_up_repeat: str = ""
        self.error_message: str = ""

        # Close pop up
        self.popup_open = False

    def build(self) -> rio.Component:
        return rio.Card(
            rio.Column(
                # Heading
                rio.Text("Create a new account", style="heading1"),
                # Display an error, if any
                rio.Banner(
                    text=self.error_message,
                    style="danger",
                    margin_top=1,
                ),
                # Form fields
                rio.TextInput(
                    text=self.bind().username_sign_up,
                    label="Username",
                    is_valid=self.username_valid,
                ),
                rio.TextInput(
                    text=self.bind().password_sign_up,
                    label="Password",
                    is_valid=self.passwords_valid,
                ),
                rio.TextInput(
                    text=self.bind().password_sign_up_repeat,
                    label="Repeat Password*",
                    is_valid=self.passwords_valid,
                ),
                # And finally, some buttons to confirm or cancel the sign-up
                # process
                rio.Row(
                    rio.Button(
                        "Sign up",
                        on_press=self.on_sign_up,
                    ),
                    rio.Button(
                        "Cancel",
                        on_press=self.on_cancel,
                    ),
                    spacing=2,
                ),
                spacing=2,
                margin=2,
            ),
            align_x=0.5,
            align_y=0.5,
            # shadow_radius=3,
        )


# </component>