make a unique key and save to a file

1. send the public key
2. client send the public key and the peerdevice details with encryption
3. server decrypt and see if it is already paired (with the key or id )
4. if paired connect the peerdevice(with peerdevice class) and update the peerdevice instance
5. if not show as a new peerdevice with paired = False

both peerdevice have each others unique identifier, so they should be okay
