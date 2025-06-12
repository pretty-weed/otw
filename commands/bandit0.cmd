grep 'The password you are looking for is' readme | sed 's;.*looking for is: \(.*\);\1;' | head -n 1
