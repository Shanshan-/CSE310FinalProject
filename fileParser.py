import sys

"""CLASSES"""
class groups:
    def __init__(self, contents):
        pass
        self.list = contents
        self.defAmt = 10
        self.ptr = 0

    #get next amt groups, or if amt == -1, get next defAmt
    #returns the next amt groups, up to last group, and empty list if none left
    def getGroups(self, amt):
        if amt == -1:
            amt = self.defAmt
        ans = []
        for num in range(0, amt):
            if num + self.ptr >= len(self.list):
                continue
            ans.append(self.list[num + self.ptr])
        return ans

    #insert a new group information in order
    def addGroup(self, groupID, groupName, numRead):
        for num in range(0, len(self.list)):
            if self.list[num] < groupID:
                continue
            else:
                self.list.insert(num, (groupID, groupName, numRead))

    #call this to reset the client groups list back to the beginning
    def reset(self):
        self.ptr = 0

class cPostsRead:
    def __init__(self, list):
        pass
        self.list = list
        self.defAmt = 10
        self.ptr = 0

    #get next amt posts, or if amt == -1, get next defAmt
    #returns the next amt groups, up to last group, and empty list if none left
    def getPosts(self, groupID, amt):
        if amt == -1:
            amt = self.defAmt
        ans = []
        for num in range(0, amt):
            if num + self.ptr >= len(self.list):
                continue
            #TODO: select out only posts whose IDs start with groupID (might need to standardize the length of groupID)
            ans.append(self.list[num + self.ptr])
        return ans

    #insert the parameter postID in order
    def addPost(self, postID):
        for num in range(0, len(self.list)):
            if self.list[num] < postID:
                continue
            else:
                self.list.insert(num, postID)

    #call this to reset the client groups list back to the beginning
    def reset(self):
        self.ptr = 0

class sPosts:
    def __init__(self, list):
        pass
        self.list = list
        self.defAmt = 10
        self.ptr = 0

    #TODO: methods to access the post information as needed

"""FUNCTIONS"""
#load groups from the file, and return in a groups class
def loadGroupFile(filename):
    _groups = []
    for line in open(filename):
        tmp = line.split()
        _groups.append(tmp)
    ans = groups(_groups)
    return ans

#load read posts from client save file
def loadClientPostFile(filename):
    posts = []
    for line in open(filename):
        tmp = line.split()
        posts.append(tmp)
    ans = cPostsRead(posts)
    return ans

#load posts detail file from server save file
def loadServerPostsFile(filename):
    posts = []
    postData = []
    x = 0
    for line in open(filename):
        if x%2 == 0:
            postData = line.split(";")
        else:
            postData.append(line)
            for num in range(0, len(postData)):
                postData[num] = postData[num].strip()
            posts.append(postData)
        x += 1
    ans = sPosts(posts)
    return ans

"""PROGRAM STARTS HERE"""
#TODO: testing and modifications of file parsing with final file format