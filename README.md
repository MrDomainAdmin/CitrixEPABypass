# Bypass Citrix EPA

This script simulates the EPA client to programatically retrieve and decrypt the requirements that it is looking for.

After running this script, it will print a list of every item that EPA is looking for. An example is:
	sys_0_MAC-MAC_ADDR_anyof_feffffffff 

After setting mac address to feffffffffff (FE:FF:FF:FF:FF:FF), Legitimately going to the Citrix EPA protected site will get you to the login page.


I wrote this script because I wasn't able to get this [script](https://github.com/Lucky0x0D/NetScalerEPABypass) working. I took the logic from their [fantastic writeup](http://lucky0x0d.com/NSEPA-Bypass.pdf) and applied it in python3. All credits to them for their fantastic research. Make sure to give them a star!
