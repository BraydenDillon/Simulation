#!/usr/bin/env python3

from icecube import dataio
import matplotlib.pyplot as plt

geometry = []
infile = dataio.I3File("PONE_10String_7Cluster_standard.i3.gz")
while infile.more():
    geometry.append(infile.pop_frame())
infile.close()

geo = geometry[0]["I3Geometry"]

# to know the object in omgeo check line 183
# GenerateNstringGCD_cluster
string_number = []
string_posx = []
string_posy = []
string_posz = []

for omkey, omgeo in geo.omgeo.iteritems():
    #print(omkey)
    #print(omkey.om)
    if omkey.string in string_number:
        continue
    string_number.append(omkey.string)
    string_posx.append(omgeo.position.x)
    string_posy.append(omgeo.position.y)
    string_posz.append(omgeo.position.z)

x = string_posx
y = string_posy
z = string_posz
strings = string_number


plt.figure(figsize=(10, 9))
plt.scatter(string_posx, string_posy, s=250, marker='o', alpha=0.5)
plt.grid(linestyle="--", linewidth=0.3)
for i, txt in enumerate(strings):
    plt.annotate(txt, (x[i], y[i]), ha='center', va='center')
plt.ylabel("y [m]", size=13)
plt.xlabel('x [m]', size=13)
plt.xlim(-600, 600)
plt.ylim(-600, 600)
plt.tight_layout()
plt.savefig("PONE_70String_10Cluster_xy.png", dpi=500)
plt.show()


# to know the object in omgeo check line 183
# GenerateNstringGCD_cluster
om_number = []
string_posx = []
string_posy = []
string_posz = []

for omkey, omgeo in geo.omgeo.iteritems():
    if omkey.om in om_number:
        continue
    print(omkey.om)
    om_number.append(omkey.om)
    string_posx.append(omgeo.position.x)
    string_posy.append(omgeo.position.y)
    string_posz.append(omgeo.position.z)

x = string_posx
y = string_posy
z = string_posz
oms = om_number

plt.figure(figsize=(4, 10))
plt.scatter(string_posx, string_posz, s=250, marker='o', alpha=0.5)
plt.grid(linestyle="--", linewidth=0.3)
for i, txt in enumerate(oms):
    plt.annotate(txt, (x[i], z[i]), ha='center', va='center')
plt.ylabel("z [m]", size=13)
plt.xlabel('x [m]', size=13)
plt.xlim(-600, 600)
plt.ylim(-600, 600)
plt.tight_layout()
plt.savefig("PONE_70String_10Cluster_xz.png", dpi=500)
plt.show()
