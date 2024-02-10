make a unique key and save to a file

1. check if network is turned off
2. make keys

3. send the public key
4. client send the public key and the peerdevice details with encryption
5. server decrypt and see if it is already paired (with the key or id )
6. if paired connect the peerdevice(with peerdevice class) and update the peerdevice instance
7. if not show as a new peerdevice with paired = False

both peerdevice have each others unique identifier, so they should be okay
