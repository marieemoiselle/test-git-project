#include <iostream>
using namespace std;

int main(){
int n, factorial = 1, i = 1;
cout << "Enter value for n: ";
cin >> n;

while(i <= n){
    factorial *= i; //factorial = factorial * i
    i++;
}

cout <<"Factorial: " << factorial;
return 0;