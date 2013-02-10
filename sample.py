import ysports

Y = ysports.YAuth()
L = ysports.YLeague(Y)

print L.name
r, c = L.scoreboard(2)
print r['status']
