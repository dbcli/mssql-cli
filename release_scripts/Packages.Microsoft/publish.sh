# Publishes deb and rpm packages to Packages.Microsoft repo

if [ -z "$1" ]
  then
    echo "Argument should be path to local repo."
    exit 1
fi

local_repo=$1
config_file=/root/.repoclient/config.json
# create tmp dir for tmp config
tmp_dir=$(mktemp -d)

# iterate through supported repos to obtain data, which we'll append to config.json.
# config.json can only hold one repo ID at a time, by doing this we can automate publishing.
for data_repo in $(cat $local_repo/release_scripts/Packages.Microsoft/supported_repos_testing.json \
 | jq -r '.[] | @base64'); do
    _jq() {
        echo ${data_repo} | base64 --decode | jq -r ${1}
    }

    # make temp config with new id value
    repo_id=$(_jq '.id')
    jq --arg a "$repo_id" '.repositoryId = $a' $config_file > $tmp_dir/tmp_config.json \
        && mv $tmp_dir/tmp_config.json $config_file
    cat $config_file
done
