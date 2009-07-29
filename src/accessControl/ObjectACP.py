#Copyright 2009 Humanitarian International Services Group
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

def getObjectACP():
    """
    params:
        str key
        str bucket
        str user
    returns:
        str ownerId
        str ownerDisplayName
        list ACP
            dict grant
                str grantee
                str granteeType
                str permission
    throws:
        InvalidKeyName
        KeyNotFound
        InvalidBucketName
        BucketNotFound
        InvalidUserName
        UserNotFound
        AccessDenied
    """


def setObjectACP():
    """
    params:
        str key
        str bucket
        str user
        list ACP
            dict grant
                str grantee
                str granteeType
                str permission
    throws:
        InvalidKeyName
        KeyNotFound
        InvalidBucketName
        BucketNotFound
        InvalidUserName
        UserNotFound
        AccessDenied
    """        


def checkUserPermission():
    """
    params:
        str key
        str bucket
        str user
        str action
    returns:
        bool permitted
    throws:
        InvalidKeyName
        KeyNotFound
        InvalidBucketName
        BucketNotFound
        InvalidUserName
        UserNotFound
        InvalidAction
    """