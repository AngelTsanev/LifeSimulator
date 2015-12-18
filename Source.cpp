#include <iostream>
#include <vector>
#include <list>
#include <time.h>
#include <string>
#include <fstream>
#include <algorithm>
#define N 10
#define M 10
using namespace std;

int B[N][M];

/*
	1-99 - има храна
	100-900 - същия пол, раса 1
	1000-9000 - другия пол, раса 1
	10000-90000 - същия пол, раса 2
	100000-900000 - другия пол, раса 2
*/

class Individual
{
	int age;
	int fitness;
	int health;
	int race;
	string goal;

	int x;
	int y;

public:
	Individual(int a, int f, int h, int r, string g, int x1, int y1) : age(a), fitness(f), health(h), race(r), goal(g), x(x1), y(y1){};
	
	void Step()
	{
		if (goal == "idle")
		{
			vector<pair<int, int>> v;
			if (x - 1 >= 0) v.push_back(pair<int, int>(x - 1, y));
			if (x + 1 < N) v.push_back(pair<int, int>(x + 1, y));
			if (y - 1 >= 0) v.push_back(pair<int, int>(x, y - 1));
			if (y + 1 < M) v.push_back(pair<int, int>(x, y + 1));

			int t = rand() % v.size();

			pair<int, int> next = v[t];

			B[x][y] -= race;
			B[next.first][next.second] += race;

			if (B[next.first][next.second] % 100) // там има храна
			{
				B[next.first][next.second]--;
				health = min(100, health + 1);
			}


			x = next.first;
			y = next.second;
			
			/*
				visualize x,y
				visualize next.first, next.second
			*/
		}
	}
};

list<Individual> l1;

fstream f;

void print_board(string s)
{
	f.open(s, ofstream::out);
	for (int i = 0; i < N; i++, f << endl) for (int j = 0; j < M; j++) f << B[i][j] << "\t";
	f.close();
}

int main()
{
	srand(time(0));

	for (int i = 0; i < N; i++) for (int j = 0; j < M; j++) B[i][j] = 0;

	for (int i = 0; i < 5; i++)
	{
		int x = rand() % N;
		int y = rand() % M;
		
		B[x][y] += 50;
	}

	for (int i = 0; i < 10; i++)
	{
		int r = pow(10, 2 + rand() % 2);
		
		int x = rand() % N;
		int y = rand() % M;

		B[x][y] += r;
		l1.push_back(Individual(1, rand() % 101, rand() % 50, r, "idle", x, y));
	}

	for (int j = 0; j < 40; j++)
	{
		for (auto i = l1.begin(); i != l1.end(); i++) i->Step();
		string ss = "step" + to_string(j) + ".txt";

		print_board(ss);
	}
	





	return 0;
}