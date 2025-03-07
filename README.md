META Workplace to MangoApps Migration Project

**Overview**

This project aims to migrate data from META Workplace to MangoApps using their respective APIs. The following data will be migrated:
- Users
- Groups
- Group Members
- Group Admins
- Group Posts
- Chats

Migration Details

**Users** - will be extracted from META Workplace and added to MangoApps with the following fields:
- Firstname
- Lastname
- Email
- EmployeeID
- Phone
- Title
- If the Email ID of the Meta user is not available, use the Meta Employee ID.

**Groups** - All groups are created by a single ADMIN user(MangoApps API Key) and this ADMIN user will be a part of the groups.
- Create groups using the API with the same name.
- If two groups have the same name, will add "_1" or "_1_2" at the end of the group name.
- Set privacy for MangoApps groups based on Meta group privacy: if the group is OPEN, set it as a Public group; otherwise, set it as Private.
- Add members to groups using the API.
- Update admin roles using the API.
- After creating Mango Groups, create a CSV with Mango Group ID and Meta Group ID.
- Fetch the Feed from Meta and update it in Mango.


**Chats** - WIP
