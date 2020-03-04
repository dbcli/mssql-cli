# Publishes deb and rpm packages to Packages.Microsoft repo

if [ -z "$1" ]
  then
    echo "First argument should be path to local repo."
    exit 1
fi

if [ ${2,,} = 'prod' ]; then
    repo_dist='prod'
elif [ ${2,,} = 'testing' ]; then
    repo_dist='testing'
else
    echo "Second argument should specify 'prod' or 'testing' for repository distribution type."
    exit 1
fi

local_repo=$1
config_file=/root/.repoclient/config.json
deb_pkg=/root/mssql-cli-dev-latest.deb
rpm_pkg=/root/mssql-cli-dev-latest.rpm

# create tmp dir for tmp config
tmp_dir=$(mktemp -d)

# iterate through supported repos to obtain data, which we'll append to config.json.
# config.json can only hold one repo ID at a time, by doing this we can automate publishing.
echo "Uploading packages to $repo_dist. Each package may take several minutes to upload."
for data_repo in $(cat $local_repo/release_scripts/Packages.Microsoft/supported_repos_$repo_dist.json \
 | jq -r '.[] | @base64'); do
    _jq() {
        echo ${data_repo} | base64 --decode | jq -r ${1}
    }

    repo_id=$(_jq '.id')
    repo_type=$(_jq '.type')
    repo_url=$(_jq '.url')

    # make temp config with new id value and then replace repoclient config
    jq --arg a "$repo_id" '.repositoryId = $a' $config_file > $tmp_dir/tmp_config.json \
        && mv $tmp_dir/tmp_config.json $config_file

    # with config updated, publish deb or rpm package
    if [ $repo_type == "apt" ]; then
        echo "Publishing .deb for $repo_url..."
        repoclient package add $deb_pkg
    elif [ $repo_type == "yum" ]; then
        echo "Publishing .rpm for $repo_url..."
        repoclient package add $rpm_pkg
    else
        echo "No package published for $(_jq '.url')"
    fi
done
