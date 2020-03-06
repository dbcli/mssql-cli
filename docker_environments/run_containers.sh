# Runs docker containers for each supported Linux distribution
# Enables easier interactive mode testing

if [ -z "$1" ]
  then
    echo "Argument should be path to local repo."
    exit 1
fi

if [ -z "$2" ]; then
    echo "Must specify folder name for Docker images. For example: 'prod'."
    exit 1
else
    docker_dir=$2
fi

local_repo=$1

for dir in $local_repo/$docker_dir/*; do
    dist_name=${dir##*/}
    tag_name=mssqlcli:$dist_name

    echo "RUNNING CONTAINER FOR: $dist_name\n"

    # run container
    docker run -it $tag_name bash
    
    echo "\n\n"
done
