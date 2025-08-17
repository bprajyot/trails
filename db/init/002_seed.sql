USE code_platform;

INSERT INTO challenges (slug, title, difficulty, description, starter_code) VALUES (
  'two-sum',
  'Two Sum',
  'easy',
  'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. Assume exactly one solution and you may not use the same element twice. Return the indices in any order.',
  JSON_OBJECT(
    'python', 'def two_sum(nums, target):\n    # Write your code here\n    return [0, 0]\n\nif __name__ == "__main__":\n    import sys, json\n    data = sys.stdin.read().strip().splitlines()\n    nums = json.loads(data[0])\n    target = int(data[1])\n    print(two_sum(nums, target))',
    'node', 'function twoSum(nums, target) {\n  // Write your code here\n  return [0, 0];\n}\n\nconst fs = require("fs");\nconst lines = fs.readFileSync(0, "utf8").trim().split(/\n/);\nconst nums = JSON.parse(lines[0]);\nconst target = parseInt(lines[1], 10);\nconsole.log(JSON.stringify(twoSum(nums, target)));',
    'cpp', '#include <bits/stdc++.h>\nusing namespace std;\nvector<int> twoSum(vector<int>& nums, int target){\n    // Write your code here\n    return {0,0};\n}\nint main(){\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n    string line; getline(cin, line);\n    // parse [1,2,3] into vector<int>
    vector<int> nums; int num=0; bool neg=false; for(char c: line){ if(c=='-'){neg=true;} if(isdigit(c)){ num = num*10 + (c-'0'); } else { if(num!=0 || neg){ nums.push_back(neg?-num:num); num=0; neg=false; } } }\n    if(num!=0 || neg){ nums.push_back(neg?-num:num);}\n    int target; cin >> target;\n    auto ans = twoSum(nums, target);\n    cout << "[" << ans[0] << "," << ans[1] << "]\n";\n    return 0;\n}'
  )
);

SET @challenge_id = LAST_INSERT_ID();

INSERT INTO test_cases (challenge_id, input_text, expected_output, is_hidden) VALUES
(@challenge_id, '[2,7,11,15]\n9', '[0,1]', 0),
(@challenge_id, '[3,2,4]\n6', '[1,2]', 0),
(@challenge_id, '[3,3]\n6', '[0,1]', 1),
(@challenge_id, '[1,5,3,7]\n8', '[1,2]', 1);