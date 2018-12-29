import requests
from flask import Flask, request

class GroupMeBot():
    """
    A simple GroupMe bot that allows you to specify commands like flask routes.
    Uses Flask under the hood to create HTTP server that listens for chat posts.
    """

    def __init__(self, bot_id):
        """
        bot_id: Your bot ID from GroupMe dev site. Used for posting replies
        """

        self._bot_id = bot_id
        self._commands = {}
        self._flask = Flask("GroupMeBot")

        @self._flask.route('/', methods=['GET', 'POST'])
        def _callback():
            """
            Default flask route that listens for new messages. On a new message,
            it makes sure to have the first /, checks if it's a valid command,
            and then calls the function for that command.
            """

            # Grab the posted message from the posted JSON
            message_text = request.get_json()['text']

            if message_text[0] == '/':

                # If there are multiple spaces, GroupMe turns some of them into
                # \xa0. I'm not sure why. Replace them with a space
                message_text = message_text.replace(u'\xa0', ' ')


                # The command should be the first word (split by whitespace),
                # while the arguments will be passed as a list

                split_message = message_text.lower().split()

                command = split_message[0]

                command_args = []
                if len(split_message) > 1:
                    command_args = split_message[1:]


                # Attempt to get the command and call it
                command_function = self._commands.get(command)

                if command_function:
                    command_function(command_args)

            # Return an okay response (No content: 204)
            return '', 204

    def command(self, command_str):
        """
        Decorator to add commands to the bot. Used like:
            @bot.command('/command')
        """

        def decorator(f):
            # Keep track of the command string and it's function in _commands dict
            self._commands[command_str] = f
            return f

        return decorator

    def serve(self, *args, **kwargs):
        """
        Start the GroupMe bot. All arguments are passed directly to Flask,
        so debugging, port, host, etc can be set
        """

        self._flask.run(*args, **kwargs)

    def post(self, message):
        """
        Post a message to the GroupMe.
        """

        data = {
            "bot_id": self._bot_id,
            "text": message
        }

        requests.post("https://api.groupme.com/v3/bots/post", data=data)
