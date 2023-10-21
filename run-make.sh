#!/usr/bin/env bash
#

if [ $# -lt 1 ]
then
	usage="This is a make wrapper that loads env variables from /etc/food/food.env, ~/.food.env, .food.env, \${food_CONF_ENV_LAST_RESORT} before calling make. Last declared env variable value overrides previous values. Eg: run-make.sh run"
	echo $usage;
	exit -1
fi

pushd .
cd -P -- "$(dirname -- "$0")"

set -o allexport

if [ -f .env ]
then
    source .env
fi

set +o allexport
make $@
popd