# Publishes deb and rpm packages to Packages.Microsoft repo

# Validate initial argument is used
if [ -z "$1" ]
  then
    echo "First argument should be path to local repo."
    exit 1
fi

# Validate second argument specifices either prod or testing for publishing channel
if [ ${2,,} = 'prod' ]; then
    repo_dist='prod'
elif [ ${2,,} = 'testing' ]; then
    repo_dist='testing'
else
    echo "Second argument should specify 'prod' or 'testing' for repository distribution type."
    exit 1
fi

local_repo=$1
deb_pkg=/root/mssql-cli_*.deb
rpm_pkg=/root/mssql-cli-*.rpm

# specificies destination testing repos for publishing
repo_url_testing=( \
    "microsoft-ubuntu-trusty-prod" \
    "microsoft-ubuntu-xenial-prod" \
    "microsoft-debian-jessie-prod" \
    "microsoft-debian-stretch-prod" \
    "microsoft-opensuse42.3-testing-prod" \
    "microsoft-rhel7.1-testing-prod" \
    "microsoft-rhel7.3-testing-prod" \
    "microsoft-rhel7.2-testing-prod" \
    "microsoft-rhel7.0-testing-prod" \
    "microsoft-rhel7.4-testing-prod" \
    "microsoft-centos7-testing-prod" \
    "microsoft-opensuse42.2-testing-prod" \
    "microsoft-sles12-testing-prod" \
    "microsoft-ubuntu-bionic-prod" \
    "microsoft-ubuntu-cosmic-prod" \
    "microsoft-ubuntu-disco-prod" \
    "microsoft-rhel8.0-testing-prod" \
    "microsoft-debian-buster-prod" \
    "microsoft-centos8-testing-prod" \
    "microsoft-debian-jessie-prod" \
    "microsoft-debian-stretch-prod" \
)

# specificies destination prod repos for publishing
repo_url_prod=( \
    "microsoft-ubuntu-trusty-prod" \
    "microsoft-ubuntu-xenial-prod" \
    "microsoft-rhel7.1-prod" \
    "microsoft-rhel7.2-prod" \
    "microsoft-rhel7.0-prod" \
    "microsoft-centos7-prod" \
    "microsoft-ubuntu-bionic-prod" \
    "microsoft-centos8-prod" \
    "microsoft-debian-jessie-prod" \
    "microsoft-debian-stretch-prod" \
)

# for each url, append to string used later as a boolean in a query
url_match_str=""
for i in ${!repo_url_testing[@]}; do
    repo_url=${repo_url_testing[i]}

    if [ $i == 0 ]; then
        url_match_str=".url==\"${repo_url}\""
    else
        url_match_str="${url_match_str} or .url==\"${repo_url}\""
    fi
done

# construct string for select statement in jq command,
# filters by repo URL and distribution type
select_stmnt="select((${url_match_str}) and .distribution==\"${repo_dist}\")"

# query for list of IDs from repo urls
list_repo_id=$(repoclient repo list | jq -r ".[] | ${select_stmnt} | @base64")
for repo_data in $(echo "${list_repo_id}"); do
    _jq() {
        # decode JSON
        echo ${repo_data} | base64 --decode | jq -r ${1}
    }
    repo_id=$(_jq '.id')
    repo_type=$(_jq '.type')

    # publish deb or rpm package
    # '-r' specifies the destination repository (by ID)
    # 'break' exits loop if something failed with command
    if [ $repo_type == "apt" ]; then
        echo "Publishing .deb for $repo_url..."
        repoclient package add $deb_pkg -r $repo_id || break
    elif [ $repo_type == "yum" ]; then
        echo "Publishing .rpm for $repo_url..."
        repoclient package add $rpm_pkg -r $repo_id || break
    else
        echo "No package published for $(_jq '.url')"
    fi
done
