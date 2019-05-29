import argparse


class Command:

    __attributes__ = [
        "name",
        "aliases",
        "arguments",
        "help",
    ]

    def __init__(self, subparsers):
        # Copy all meta parameters of the command into the __meta__ dictionary,
        # so it can be accessible during the setup of commands.
        attrs = {attr: getattr(self, attr, None)
                 for attr in self.__attributes__}

        self.__meta__ = argparse.Namespace(**attrs)
        self.subcommands = {}

        self.subparser = subparsers.add_parser(
            name=self.__meta__.name,
            help=self.__meta__.help,
            aliases=(self.__meta__.aliases or []))

        for args, kwargs in self.__meta__.arguments or []:
            self.subparser.add_argument(*args, **kwargs)

        class_dict = self.__class__.__dict__
        filter_predicate = lambda o: isinstance(o, type)

        # Search for sub-classes
        subcommands = filter(filter_predicate, class_dict.values())
        subcommands = list(subcommands)

        # At least print the help message for the command.
        self.subparser.set_defaults(func=self.handle)

        subparsers = self.subparser.add_subparsers()
        for command_class in subcommands:
            command = command_class(subparsers)
            self.subcommands[command_class.__name__] = command

    def handle(self, context):
        self.subparser.print_help()



class App:

    def __init__(self, prog, modules):
        self.parser = argparse.ArgumentParser(prog=prog)
        self.parser.set_defaults(func=lambda *x: self.parser.print_help())
        subparsers = self.parser.add_subparsers()

        self.modules = [m(subparsers) for m in modules]

    def argument(self, args, kwargs):
        self.parser.add_argument(*args, **kwargs)

    def start(self):
        args = self.parser.parse_args()
        args.func(argparse.Namespace(args=args))
