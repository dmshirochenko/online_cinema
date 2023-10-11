# Authentication Service

## Descritpion

The service provides basic authorization and authentication logic for managing users. Existing functionality:
1. User authorization: sign-up, login, logout endpoints
2. Authenticatihon required resources: getting user login history
3. Roles management (admin role is required): creating, editing, listing and deleting roles.
4. User-Role management (admin role is required): asssigning and removing a role to/from a user.

Swagger Documentation is available at `http://127.0.0.1:5001/apidocs/`:

![Screenshot 2023-05-08 at 6 07 27 PM](https://user-images.githubusercontent.com/23639048/236888970-ef270216-cfc3-44c0-b24c-17cc141f0bf6.png)

## Endpoints

__User Authorization__
* `/auth/api/v1/login` - login endpoint
* `/auth/api/v1/logout` - logout endpoint
* `/auth/api/v1/signup` - sign up endpoint

__Authentication-required routes__
* `/auth/api/v1/login_history/{page}` - show user's history
* `/auth/api/v1/role_exists` - get user's info including their role
* `/auth/api/v1/user/{user_id}` [get] - get user's info
* `/auth/api/v1/users` - list all existing users
* `/user/api/v1/user/{user_id}` [delete] - delete existing user

__Admin CRUD__
* `/auth/admin/all_roles` - list all existing roles
* `/auth/admin/create_role` - create a new role
* `/auth/admin/delete_role/{role}` - delete an existing role
* `/auth/admin/edit_role` - edit an existing role

__Admin Roles Management__
* `/auth/admin/assign_user_role` - assign existing role to a user
* `/auth/admin/remove_user_role` - remove existing role from a user

## How to run

### Service

Configure docker-compose.override.yaml file for either developer or pruduction settings.
* `docker-compose up -d --build`

__Creating Superuser from CLI__: `flask create-user admin`

### Tests
* `cd auth/tests`
* `docker-compose up -d build`

