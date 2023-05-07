package subscription

## Playground: https://play.openpolicyagent.org/p/f5TzJLiA88
import future.keywords.in
import future.keywords.every
import data.subscription.plan_features

default allow = false
default plan = "free"

## Get current plan
plan = current_plan {
	input.user.current_plan != ""
	current_plan := input.user.current_plan
}

## Get current features for user plan
features = data.subscription.plan_features[plan]

## Check features has in plan or not
not_allowed_features[ftn] {
	some key, _ in input.check_features
    not features[key]
    ftn := key
}

## Deny check for feature limitation
## Return deny message
## @TODO: needs update more deny rules here

deny[msg] {
    input.check_features.file_capacity
	input.check_features.file_capacity >= features.file_capacity
    msg := sprintf("Your plan cannot process file larger than %vMb", [(features.file_capacity / 1048576)])
}

deny[msg] {
    input.check_features.cloud_space_total_file
	input.stats.cloud_space_total_file >= features.cloud_space_total_file
    msg := sprintf("Your plan cannot upload more than %v items", [features.cloud_space_total_file])
}

deny[msg] {
    input.check_features.pdf_manipulation_per_month
	input.month_stats.pdf_manipulation_per_month >= features.pdf_manipulation_per_month
    msg := sprintf("Your plan cannot process more than %v pdf manipulation per month", [features.pdf_manipulation_per_month])
}

deny[msg] {
    count(not_allowed_features) > 0
    msg := sprintf("Features not allowed: %v", [not_allowed_features])
}

## Final decision
allow {
	count(not_allowed_features) == 0
    count(deny) == 0
}

## To return more data in a rule, combine all decision to an object
response := {
    "allow": allow,
    "deny": deny,
    "not_allow_features": not_allowed_features,
    # "features": features,
    "plan": plan
}