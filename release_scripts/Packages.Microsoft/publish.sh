# Publishes deb and rpm packages to Packages.Microsoft repo

# Validate initial argument is used
if [[ -z "$1" ]]
  then
    echo "First argument should be path to local repo."
    exit 1
fi

# Validate second argument specifices either prod or testing for publishing channel.
# Each dictionary specifies key-value paris for repo URLs with distribution names.
# Both URL and distribution are needed to query for a repo ID, which is later used
# for publishing.
if [[ ${2,,} = 'prod' ]]; then
    declare -A repos=( \
        ["microsoft-ubuntu-trusty-prod"]="trusty" \
        ["microsoft-ubuntu-xenial-prod"]="xenial" \
        ["microsoft-rhel7.0-prod"]="trusty" \
        ["microsoft-rhel7.1-prod"]="trusty" \
        ["microsoft-rhel7.2-prod"]="trusty" \
        ["microsoft-centos7-prod"]="trusty" \
        ["microsoft-ubuntu-bionic-prod"]="bionic" \
        ["microsoft-debian-jessie-prod"]="jessie" \
        ["microsoft-debian-stretch-prod"]="stretch" \
    )
elif [[ ${2,,} = 'testing' ]]; then
    declare -A repos=( \
        ["microsoft-ubuntu-trusty-prod"]="testing" \
        ["microsoft-ubuntu-xenial-prod"]="testing" \
        ["microsoft-debian-jessie-prod"]="testing" \
        ["microsoft-debian-stretch-prod"]="testing" \
        ["microsoft-opensuse42.3-testing-prod"]="testing" \
        ["microsoft-rhel7.0-testing-prod"]="testing" \
        ["microsoft-rhel7.1-testing-prod"]="testing" \
        ["microsoft-rhel7.3-testing-prod"]="testing" \
        ["microsoft-rhel7.2-testing-prod"]="testing" \
        ["microsoft-rhel7.4-testing-prod"]="testing" \
        ["microsoft-rhel8.0-testing-prod"]="testing" \
        ["microsoft-centos7-testing-prod"]="testing" \
        ["microsoft-centos8-testing-prod"]="testing" \
        ["microsoft-opensuse42.2-testing-prod"]="testing" \
        ["microsoft-sles12-testing-prod"]="testing" \
        ["microsoft-ubuntu-bionic-prod"]="testing" \
        ["microsoft-ubuntu-cosmic-prod"]="testing" \
        ["microsoft-ubuntu-disco-prod"]="testing" \
        ["microsoft-debian-buster-prod"]="testing" \
        ["microsoft-debian-jessie-prod"]="testing" \
        ["microsoft-debian-stretch-prod"]="testing" \
    )
else
    echo "Second argument should specify 'prod' or 'testing' for repository distribution type."
    exit 1
fi

# Confirm if third optional '--print' argument is used
if [[ ${3,,} = '--print' ]]; then
    is_print='True'
else
    is_print='False'

    # download latest stable deb and rpm packages
    wget https://mssqlcli.blob.core.windows.net/daily/deb/mssql-cli_1.0.0-1_all.deb --directory-prefix=/root/
    wget https://mssqlcli.blob.core.windows.net/daily/rpm/mssql-cli-1.0.0-1.el8.x86_64.rpm --directory-prefix=/root/
fi

local_repo=$1
deb_pkg=/root/mssql-cli_1.0.0-1_all.deb
rpm_pkg=/root/mssql-cli-1.0.0-1.el8.x86_64.rpm

# build url_match_string to get repo ID's from above URL names
url_match_str=""
for repo_url in ${!repos[@]}; do
    # get key from url string
    distribution="${repos[$repo_url]}"

    if [[ $url_match_str == "" ]]; then
        # only append 'or' to string if not first index
        url_match_str="(.url==\"${repo_url}\" and .distribution==\"${distribution}\")"
    else
        url_match_str="${url_match_str} or (.url==\"${repo_url}\" and .distribution==\"${distribution}\")"
    fi
done

# construct string for select statement in jq command,
# filters by repo URL and distribution type
select_stmnt="select(${url_match_str})"

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
    if [[ $repo_type == "apt" ]]; then
        command="repoclient package add $deb_pkg -r $repo_id"
    elif [[ $repo_type == "yum" ]]; then
        command="repoclient package add $rpm_pkg -r $repo_id"
    else
        echo "No package published for $(_jq '.url')"
        break
    fi

    echo $command
    if [[ $is_print != "True" ]]; then
        # publish package
        echo "Publishing $repo_type for $repo_url..."
        eval "$command || break"
        printf "\n"
    fi
done
