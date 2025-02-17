import os
import jinja2
import pwd
import argparse
import subprocess  # For git command

def generate_service_file(project_path, env_name, user):
    """Generates a systemd service file from a Jinja2 template.

    Args:
        project_path: The absolute path to your project directory.
        env_name: The name of your conda environment.
        user: The username on the Raspberry Pi.

    Returns:
        The generated service file content as a string.
    """

    # 1. Jinja2 Environment and Template Loading
    template_dir = os.path.dirname(os.path.abspath(__file__)) # Directory where script is
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template("robot-control.service.j2")  # Template file name

    # 2. Context for the Template
    context = {
        "project_path": project_path,
        "env_path": os.path.join(os.path.expanduser("~"), ".conda", "envs", env_name),  # Construct conda env path
        "user": user,
    }

    # 3. Render the Template
    service_file_content = template.render(context)
    return service_file_content


def write_service_file(service_file_content, output_path):
    """Writes the generated service file content to the specified output path.

    Args:
        service_file_content: The content of the service file.
        output_path: The path where the service file should be written.
    """

    with open(output_path, "w") as f:
        f.write(service_file_content)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate systemd service file.")
    parser.add_argument("-p", "--project_path", help="Absolute path to your project directory (optional, defaults to Git root).")
    parser.add_argument("-e", "--env_name", help="Name of your conda environment (optional, defaults to active environment).")
    parser.add_argument("-u", "--user", help="Username on the Raspberry Pi (optional, defaults to current user).", default=None)
    parser.add_argument(
        "-o",
        "--output",
        help="Output path for the.service file (optional, defaults to /etc/systemd/system/robot-control.service).",
        default="robot-control.conf"
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
    if args.env_name:
        env_name = args.env_name
    else:
        env_name = get_active_conda_env_path()
        if env_name is None:
            raise ValueError("No conda environment is active. Please activate one or provide the environment name with -e/--env_name.")
        else:
            print(f"Using active conda environment: {env_name}")


    output_path = args.output

    service_file_content = generate_service_file(project_path, env_name, user)
    write_service_file(service_file_content, output_path)

    print(f"Service file generated and written to: {output_path}")
    print(f"User used: {user}")
    print(f"Environment used: {env_name}")
    print(f"Project path used: {project_path}")
