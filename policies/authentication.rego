package authentication
import future.keywords.in

default approveJira = false
default isAllowedToCreatePr = false
default isUserLoggedIn = false

authentic_users := ["sanjeev", "himangshu","divya","pralave","nisha","tathya"]
# user_role := {
#     "himangshu" : ["IT_DEVELOPER","IT_QA_ADMIN"],
#     "sanjeev" : ["IT_DEVELOPER","IT_QA_ADMIN","ADMIN"],
#     "tathya" : ["IT_DEVELOPER"],
#     "pralave" : ["ADMIN"]
# }

approveJira{
    isUserLoggedIn
    isJiraUserAuthorized
    input.jira.type == "requirement"
    isJiraLinkedWithPR
    isJiraDescFieldNotEmpty 
    isJiraUserAuthorized   
}

isUserLoggedIn{
    input.user != "None"
}

isUserAuthorized{
    input.user.permissions[i] == "EMPLOYEE"
}

isJiraDescFieldNotEmpty{
    count(input.jira.descriptions) != 0
}

isJiraUserAuthorized{
    containsRole  
}

containsRole{
    permissions := input.user.permissions
	permissions[i] == "IT_DEVELOPER"
    permissions[j] == "IT_QA_ADMIN"
}

containsRole{
	permissions := input.user.permissions
    permissions[i] == "ADMIN"
}

isJiraLinkedWithPR{
    input.jira.pullRequestID in input.pullRequestIDs
}

isAllowedToCreatePr {
	input.user.username in authentic_users
}