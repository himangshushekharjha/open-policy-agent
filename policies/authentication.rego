package authentication

default loginAllow = false
default createBlogAllow = false

loginAllow {
    input.user != "None"

}

# createBlogAllow{
#     # loginAllow == true
#     input.user.permissions[_] == "morgan_blogger"
# }

