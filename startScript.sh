#!/bin/bash
cd "$(dirname "$0")";

# Function to create a directory with appropriate permissions
create_dir_with_perms() {
  local dir_path="$1"
  if [[ ! -d "$dir_path" ]]; then
    mkdir -p "$dir_path"
    chmod 755 "$dir_path"  # Set appropriate permissions (modify if needed)
  fi
}

# Check for required arguments (name and testid)
if [ $# -ne 1 ]; then
  echo "Usage: $0 <testid>"
  exit 1
fi

# Get name and testid from arguments
testid="$1"

# Ensure containers directory exists in the current working directory
containers_dir="./containers"  # Adjusted to create in current working directory
create_dir_with_perms "$containers_dir"

# Create testid directory inside containers
testid_dir="$containers_dir/$testid"
create_dir_with_perms "$testid_dir"

# Create subdirectories inside testid_dir
for i in {1..2}; do
  sub_dir_name="container_${testid}_${i}"
  sub_dir_path="$testid_dir/$sub_dir_name"
  create_dir_with_perms "$sub_dir_path"
  cd $sub_dir_path
  /usr/local/bin/docker run -d -it --name $sub_dir_name -v "$PWD":/src python bash
  cd ..
  cd ..
  cd ..
done

echo "Directories created successfully!"
