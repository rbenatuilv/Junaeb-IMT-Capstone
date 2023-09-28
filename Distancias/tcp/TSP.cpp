#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const int MAXN = 12;
ll INF = 1e18;
int n;
ll adj[MAXN][MAXN];
ll dp[1 << MAXN][MAXN];
ll x[MAXN];
ll y[MAXN];

ll DP(int mask, int v){
    
    if(mask == (1<<n) - 1){
        return adj[v][0];
    }
    if(dp[mask][v] != -1){
        return dp[mask][v];
    }

    dp[mask][v] = INF;

    for(int u = 0; u<n; u++){
        if((mask&(1<<u)) == 0){
            dp[mask][v] = min(dp[mask][v], adj[v][u] + DP(mask|(1<<u), u));
        }
    }
    
    return dp[mask][v];
}

int main(){

    cin>>n;

    for(int i = 0; i<n; i++){
        cin>>x[i]>>y[i];
    }

    for(int i = 0; i<n; i++){
        for(int j = 0; j<n; j++){
            adj[i][j] = abs(x[i] - x[j]) + abs(y[i] - y[j]);
        }
    }

    memset(dp, -1, sizeof dp);
    
    cout<<DP(1, 0)<<"\n";
    
    return 0;
}