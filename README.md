# Cobbler

This is a directory for building a Cobbler server using Vagrant, Docker
and various scripts and provisioners.

## How Cobbler is designed

The configuration structure of Cobble is based on a set of registered objects.
Each object represents an entity that is associated with another entity. When
one object points to another object, it inherits the data of the pointed object
and can override or add more specific information. The following types of objects
are defined:
 
   **Distribution**: Represents an operating system. It carries information about
    the kernel and initrd, plus other data such as kernel parameters.
    
   **Profile**: Points to a distribution, a kickstart file, and possibly 
    repositories, plus other data such as more specific kernel parameters.
    
   **System**: Represents the machine to be provisioned. It points to a profile
    or an image and contains information about IP and MAC addresses, power 
    management and more specialized data.
    
   **Repository**: Holds mirroring information for a yum or rsync repository.
   
   **Image**: Can replace a distribution object for a files that do not fit in 
    this category.

   **Cobbler Object Relationships**:
    
   ![Cobbler Object Relationships Image](Provision/Cobbler/cobbler.png)

## Using Cobbler

The options to configure and use Cobbler include command line, API, XML_RPC and
it's web interface.

Cobbler has packages for many Linux distributions. We will base these instructions
for Ubuntu system - 

```
 sudo apt-get install cobbler cobbler-web debmirror mkisofs 
```
   

After installation, it is always great idea to check cobbler's configuration to
see if everything is as it should. Cobbler provides the command

```
 sudo cobbler check
```

THe cobbler-web should be installed in location **/etc/apache2/conf.d/cobbler_web.conf**
file that configures Apache to run the Cobbler web interface.

The cobbler web interface is served by apache at **http:// <hostname\>/cobbler_web**. 
If cobbler does not prompt for a password, it should set the default
username/password to **cobbler/cobbler**.
If this default does not work, we can set the password by running

``` 
 htdigest /etc/cobbler/users.digest "Cobbler" cobbler
```

this will prompt us for a new password. Once we have updated the password, we 
must run 

```
cobbler sync
```

## Configuring Cobbler

The main configuration file is under **/etc/cobbler/settings**. Most of the options
are self explanatory. 

Make sure the options listed below are set as such:

   * manage_dhcp: 1
   * manage_dns: 1
   * manage_tftpd: 1
   * restart_dhcp: 1
   * restart_dns: 1
   * pxe_just_once: 1
   * next_server: <server's IP address>
   * server: <server's IP address>
   
The option **next_server** is used in the **DHCP** configuration
file to tell the machines what is the address of the server that provides the boot
file.
The option **server** is used during the machine installation to refer to
the Cobbler server address.
Finally, the option **pxe_just_once** prevents 
installation loops in machines that are configure to always boot from the network.

Now that cobbler knows which services to manage, we must tell it which programs
to use. The options are as follows:

   * DHCP: ISC dhcpd or dnsmasq
   * DNS: BIND or dnsmasq
   * TFTP: in.tftpd or cobbler's internal TFTP

For our setting we will use ISC_dhcpd and in.tftpd. [DNS TBD]. Edit the file
under in folder **/etc/cobbler/modules.conf** and make sure it include
the statements below:

    [dhcp]
    module = manage_isc

    [tftpd]
    module = manage_in_tftpd
   
Install the services

```
 apt-get install isc-dhcp-server
```

and

```
 apt-get install xinetd  tftpd tftp
```
        
Cobbler uses a template to create the configuration files for these services. Editing
the template files locate under **/etc/cobbler** is necessary to adjust the network 
information such as the gateway address and IP range.

Edit the **dhcp.template** file accordingly(i.e set the subnet, ip-range, gateway etc.)
Show below is an example of the subnet setting from a dhcp.template file

```
subnet 192.168.2.0 netmask 255.255.255.0 {
     range 192.168.2.110 192.168.2.115
     option gateway 192.168.2.1
     option broadcast-address 192.168.2.255
     option domain-name-servers 192.168.2.1 10.70.7.7 10.70.7.6
     option subnet-mask         255.255.255.0;
     default-lease-time         21600;
     max-lease-time             43200;
     next-server                $next_server;
```

For the **tftpd.template** file, make sure you have the settings set as show below:

```
service tftp
{
        disable                 = no
        socket_type             = dgram
        protocol                = udp
        wait                    = yes
        user                    = $user
        server                  = $binary
        server_args             = -s /var/lib/tftpboot
        per_source              = 11
        cps                     = 100 2
        flags                   = IPv4
}
```






## Installing Ubuntu System

To add Ubuntu installation tree, first we download the ISO media and the run the 
following commands to mount the media and extract content.

```
mount -o loop ubuntu-14.04-x86_64.iso /mnt/iso
```

Cobbler now copies the media content to the filesystem. This operation may take a
while.


## Creating a Distro

```
cobbler import --arch=x86_64 --path=/mnt/iso --name=ubuntu14
```

The **cobbler import** automatically creates a distribution and a profile
object for us. We can also point Cobbler to a network repository.


## Creating a Profile

First step to creating a profile is specifying a *kickstart* file, that is based
on the file available from **/var/lib/cobbler/kickstarts**. In this file,
under the section **%packages**, define a variable **$desktop_pkg_group**, which
will alter be substituted to determine which packages are installed. Cobbler will
know the value, because we will define it under the option **ksmeta**.

We have the option of creating a profile for *Xfce* or *GNOME*. The command are
listed below, respectively:

xfce option
```
 cobbler profile add --name=ubuntu14  
                     --ksmeta='desktop_pkg_group=@xfce-desktop'  
                     --kickstart=/var/lib/cobbler/kickstarts/example.ks   
                     --parent=ubuntu-x86
```


GNOME option
``` 
cobbler profile add --name=ubuntu14  
                        --ksmeta='desktop_pkg_group=@gnome-desktop'  
                        --kickstart=/var/lib/cobbler/kickstarts/example.ks   
                        --parent=ubuntu-x86_64
```
      
                                                                               
```
 cobbler profile report
```
 
The **--parent** parameter tell the profile to inherit from the Ubuntu Profile.
To verify the kickstarter content, we can use the command:

``` 
cobbler profile getks --name=ubuntu14
```


## Associating machines with Profiles

The last step in the setup is associating a machine with the profile we want them
installed with. The command is :

``` 
cobbler system add --name=desktop-xfce-1 --profile=ubuntu-xfce -mac=<MAHCHINE MAC ADDRESS>
```


```
 cobbler system report
```

The power management feature in Cobbler can power on, power off and reboot the
machine for us. This function is also useful when we have many machines and 
must organize power management information such as user and passwords for each
because Cobbler registers them in its base. Suppose machine desktop-xfce-1 is in
an IBM Bladecenter at location bay2 and desktop-gnome-1 is a machine that is managed 
with an RSA board, we can set up our system as seen below

xfce option
```
 cobbler system edit --name=desktop-xfce-1 \
                     --power-type=bladecenter \
                     --power-id=2 \
                     --power-user=admin_user \
                     --power-pass=admin_password \
                     --power-address=192.168.122.2
```
   
   
GNOME option                  
``` 
cobbler system edit --name=desktop-gnome-1 \
                    --power-type=rsa \
                    --power-user=rsa_user \
                    --power-pass=rsa_password \
                    --power-address=192.168.122.3
```                   
 

We should always remember to apply our changes to the file system

```
 cobbler sync
```

## Starting the installation

We are ready to boot the machines and install them. They must be configured to boot
from the network. 

```
 cobbler system reboot --name=desktop-xfce-1
```


## Cobbler: the web-interface

Cobbler offers a useful web interface, which allows us to do everything via the 
web


## Customizable Security

For communicating with cobbler remotely, via the web or xmlrpc, we have different
authentication systems and different workflows. The settings for authentication
and authorization is governed in the settings in **/etc/cobbler/modules.conf**

### Authentication

The default format for authentication is set to deny all. This disables all
external modifications(eg apis) and disables cobbler web interface. Cobbler provides six
modes of authentication settings


   **DIGEST**: This option simply uses a file to identify the username and password
   information. We can always add more users by running the command
   
   ```
    htdigest /etc/cobbler/users.digest "Cobbler" $username
   ```
   
   **kERBEROS**: This option lets cobbler defer the decision to Apace. We can
   modify it to do things other than Kerberos.
   [more info](https://fedorahosted.org/cobbler/wiki/CobblerWithKerberos)
   
   **LDAP**: This option authenticates against LDAP using the settings under **/etc/cobbler/settings**.
   The direct cobbection to LDAP does not rely on Apache.
   [more info](https://fedorahosted.org/cobbler/wiki/CobblerWithLdap)
   
   **SPACEWALK**: This option uses [spacewalk](http://fedorahosted.org/spacewalk) for the
   authorization scheme to login to cobbler, since Spacewalk uses cobbler service.
   
   **TESTING**: This option is to be used during the development and never in production.
   Only the combination testing/testing is allowed and no other.
   
   **USER SUPPLIED**: This option is for users programming their own module to 
   handle to authentication.
   [more info](https://fedorahosted.org/cobbler/wiki/CobblerModule)

[more info](https://fedorahosted.org/cobbler/wiki/CustomizableAuthentication)

### Authorization 

We discuss the limit of access to users to specific aspects of Cobbler. The authorization
happens once users are authenticated. Authorization choices are also set in the
**/etc/cobbler/modules.conf** document.

We have 3 different modes of authorizations:

   **Allow All**: This module permits any user who has passed the authorization step.
   This step is not recommended if you are authenticating using LDAP
   
   **Config File**: This uses a simle file in **/etc.cobbler/users.conf** to 
   provide a list of what users can access. Users not in this file will hot have access.
   
   **Owenership**: This is similar to config-file but the enforcement is dynamic.
   This allows to keep users from modifying distros or profiles and system records.
   This is a good choice for use of cobbler in large companies. [More detail](https://fedorahosted.org/cobbler/wiki/CustomizableAuthorization)

   **Users Supplied Modules**: This allows users to create a custom, more refined,
   access control. [See here](https://fedorahosted.org/cobbler/wiki/CobblerModule)

   **File Format**: This file **/etc/cobbler/users.conf** is ignored by defaults as
   the default modes are to allow all, but if we choose other modes, we can use this file
   to configure alternative authentication modes for the different options listed above

More explanation is given [here.](https://fedorahosted.org/cobbler/wiki/CustomizableAuthorization)
   
## Cobbler APIs

Cobbler has a python api named __cobbler__, however, it strongly advices using the
__CobblerXmlrpc__ interface  instead. We will only discuss the use of the xmlrpc.

To use Cobbler's XMLRPC API, first we must setup the Customizable Security(see above)
and ensure that Apace and cobbler are running on our server.

### Connecting and Logging In


We first define our connection with Cobbler xmlrpc api, and then we login. We
get a token which expires every 60min. Once this token expires it is necessary to
renew it for subsequent api calls.

The api provides information on the distros, systems, profiles, images and repos 
that are currently available. We can also do search, make changes, create new objects,
remove objects, power management and much more. [more info](https://fedorahosted.org/cobbler/wiki/CobblerXmlrpc)

```
import xmlrpclib

server = xmlrpclib.Server("http://192.168.2.199/cobbler_api")
token = server.login("cobbler","cobbler")

# Create a distro
distro_id = remote.new_distro(token)
remote.modify_distro(distro_id, 'distro1',   'example-distro',token)
remote.modify_distro(distro_id, 'kernel', '/opt/stuff/vmlinuz',token)
remote.modify_distro(distro_id, 'initrd', '/opt/stuff/initrd.img',token)
remote.save_distro(distro_id,token)

# Remove a distro
remote.remove_profile("distro1",token)
```

XMLRPC binds to localhost on port 25150 by default and uses a separate log file
located at **/var/log/cobbler/cobblerd.log**, where remote exceptions are logged here.

The source code for the api is found [here](https://madhatter.googlecode.com/hg/cobbler/remote.py).
It is instructive to through the code, especially the test section at the bottom.
