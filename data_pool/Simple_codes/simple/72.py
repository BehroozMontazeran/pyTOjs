def majorityNumber(nums):
    num_count = {}
    for num in nums:
        if num in num_count:
            num_count[num] += 1
        else:
            num_count[num] = 1
    for num in num_count:
        if num_count[num] > len(nums) / 2:
            return num
    return - 1


a = [2, 2, 1, 1, 1, 2, 2]
print (majorityNumber(a))
