import os
import jinja2
import pwd
import argparse
import subprocess  # For git command
import netifaces  # For IP address

def get_active_conda_env_path():
    """Gets the path of the currently active conda environment.

    Returns:
        The path to the active conda environment, or None if no environment is active.
    """

    # Get the value of the CONDA_PREFIX environment variable
    # This is the path to the active conda environment
    return os.environ.get("CONDA_PREFIX")

def get_git_root():
    """Gets the root directory of the current Git repository.

    Returns:
        The absolute path to the Git repository root, or None if not in a Git repository.
    """
    try:
        result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        git_root = result.stdout.strip()
        return git_root
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None  # Git not installed

def get_ip_address(interface: str = "wlan0"):
    """Gets the external IP address of the Raspberry Pi."""
    try:
        return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except KeyError:
        print(f"Valid interfaces: {netifaces.interfaces()}")  # Print available interfaces
        return None  # No IPv4 address found

def _write_service_file(service_file_content, output_path):
    """Writes the generated service file content to the specified output path.

    Args:
        service_file_content: The content of the service file.
        output_path: The path where the service file should be written.
    """

    with open(output_path, "w") as f:
        f.write(service_file_content)

class ServiceFileGenerator:
    def __init__(self, project_path, env_name, user, ip_address, out_dir: str | None = None):
        self.project_path = project_path
        self.env_name = env_name
        self.user = user
        self.ip_address = ip_address

        if out_dir is None:
            self.out_dir = os.path.join(self.project_path, "setup")
        else:
            self.out_dir = out_dir

        # Directory where script is
        self.template_dir = os.path.dirname(os.path.abspath(__file__))
        # 1. Jinja2 Environment
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir))

        # 2. Context for the Template
        self.context = {
            "project_path": self.project_path,
            "env_path": os.path.join(os.path.expanduser("~"), ".conda", "envs", self.env_name),  # Construct conda env path
            "user": self.user,
            "ip_address": self.ip_address,
        }

    def render_template(self, template_name):
        """Renders a Jinja2 template with the context.

        Args:
            template_name: The name of the Jinja2 template file.

        Returns:
            The rendered template content as a string.
        """

        # 1. Load the template
        template = self.env.get_template(template_name)

        # 2. Render the Template
        return template.render(self.context)

    def generate_service_file(self):
        """Generates a systemd service file from a Jinja2 template.

        Returns:
            The generated service file content as a string.
        """

        file = "robot-control.service"
        _write_service_file(self.render_template(file + ".j2"),
                                   os.path.join(self.out_dir, file))

    def generate_nginx_config(self):
        """Generates a systemd service file from a Jinja2 template.

        Returns:
            The generated service file content as a string.
        """

        file = "robot-control"
        _write_service_file(self.render_template(file + ".nginx.j2"),
                            os.path.join(self.out_dir, file))

    def generate_lighttpd_conf_file(self):
        """Generates a systemd service file from a Jinja2 template.

        Returns:
            The generated service file content as a string.
        """

        file = "robot-control.lighttpd.conf"
        _write_service_file(self.render_template(file + ".j2"),
                            os.path.join(self.out_dir, file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate systemd service file.")
    parser.add_argument("-p", "--project_path", help="Absolute path to your project directory (optional, defaults to Git root).")
    parser.add_argument("-e", "--env_path", help="Path to the conda environment (optional, defaults to active environment).")
    parser.add_argument("-u", "--user", help="Username on the Raspberry Pi (optional, defaults to current user).", default=None)
    parser.add_argument("-i", "--interface", nargs="*", help="Network interface to get IP address from (optional, defaults to wlan0).", default=["wlan0"])
    parser.add_argument(
        "-o",
        "--output_dir",
        help="Output path for the generated files (optional, defaults to current directory).",
        default=".",
    )

    args = parser.parse_args()

    user = args.user if args.user else pwd.getpwuid(os.getuid()).pw_name

    # Determine project_path: command line arg or git root or error
    if args.project_path:
        project_path = args.project_path
    else:
        project_path = get_git_root()
        if project_path is None:
            raise ValueError("Not in a Git repository. Please provide the project path with -p/--project_path.")
        else:
            print(f"Using Git root as project path: {project_path}")

    # Determine env_name: command line arg or active env or error (same as before)
    if args.env_path:
        env_name = args.env_path
    else:
        env_name = get_active_conda_env_path()
        if env_name is None:
            raise ValueError("No conda environment is active. Please activate one or provide the environment name with -e/--env_name.")
        else:
            print(f"Using active conda environment: {env_name}")

    ip_address = ' '.join([get_ip_address(iface) for iface in args.interface])

    output_path = args.output_dir

    print(f"Service file generated and written to: {output_path}")
    print(f"User used: {user}")
    print(f"IP address(es) used: '{ip_address}'")
    print(f"Environment used: {env_name}")
    print(f"Project path used: {project_path}")

    generator = ServiceFileGenerator(project_path, env_name, user, ip_address, out_dir=output_path)
    generator.generate_service_file()
    # generator.generate_nginx_config()
