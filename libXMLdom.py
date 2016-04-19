#!/usr/bin/python

import xml.dom.minidom

impl = xml.dom.minidom.getDOMImplementation()
dom = impl.createDocument(None, None, None)

def ce(str):
    return dom.createElement(str)

def sa(dom, s0, s1):
    dom.setAttribute(s0, s1)

def ac(dom0, dom1):
    dom0.appendChild(dom1)

def at(dom0, str):
    dom0.appendChild(dom.createTextNode(str))

def getDiskXML(file, imagetype):
    disk = ce('disk')
    sa(disk, 'type', 'file')
    if imagetype == 'qcow':
        driver = ce('driver')
        sa(driver, 'name', 'tap')
        sa(driver, 'type', 'qcow')
        ac(disk, driver)

    source = ce('source')
    sa(source, 'file', file)
    ac(disk, source)

    target = ce('target')
    sa(target, 'dev', 'hda')
    sa(target, 'bus', 'ide')
    ac(disk, target)

    return disk

def getInterfaceXML(macstr):
    interface = ce('interface')
    sa(interface, 'type', 'bridge')

    source = ce('source')
    sa(source, 'bridge', 'xenbr0')
    ac(interface, source)
    
    mac = ce('mac')
    sa(mac, 'address', macstr)
    ac(interface, mac)
    
    script = ce('script')
    sa(script, 'path', '/etc/xen/scripts/vif-bridge')
    ac(interface, script)

    return interface

def getSerialXML():
    serial = ce('serial')
    sa(serial, 'type', 'pty')

    source = ce('source')
    sa(source, 'path', '/dev/pts/3')
    ac(serial, source)

    target = ce('target')
    sa(target, 'port', '0')
    ac(serial, target)
 
    return serial

def getDevicesXML(file, imagetype, mac):
    devices = ce('devices')
    emulator = ce('emulator')
    at(emulator, '/usr/lib64/xen/bin/qemu-dm')
    ac(devices, emulator)
    
    disk = getDiskXML(file, imagetype)
    ac(devices, disk)
    
    interface = getInterfaceXML(mac)
    ac(devices, interface)

    serial = getSerialXML()
    ac(devices, serial)

    tablet = ce('input')
    sa(tablet, 'type', 'tablet')
    sa(tablet, 'bus', 'usb')
    ac(devices, tablet)

    mouse = ce('input')
    sa(mouse, 'type', 'mouse')
    sa(mouse, 'bus', 'ps2')
    ac(devices, mouse)

    graphics = ce('graphics')
    sa(graphics, 'type', 'vnc')
    sa(graphics, 'port', '-1')
    sa(graphics, 'autoport', 'yes')
    sa(graphics, 'keymap', 'en-us')
    sa(graphics, 'listen', '0.0.0.0')
    ac(devices, graphics)
    return devices

def getDomainXML(namestr, mem, vcpus, file, imagetype, mac):
    domain = ce('domain')
    sa(domain, 'type', 'xen')

    name = ce('name')
    at(name, namestr)
    ac(domain, name)

    os = ce('os')
    type = ce('type')
    at(type,'hvm')
    ac(os, type)
    loader = ce('loader')
    at(loader, '/usr/lib/xen/boot/hvmloader')
    ac(os, loader)
    ac(domain, os)

    features = ce('features')
    ac(features, ce('acpi'))
    ac(features, ce('apic'))
    ac(features, ce('pae'))
    ac(domain, features)
    
    clock = ce('clock')
    sa(clock, 'offset', 'localtime')
    ac(domain, clock)
    
    on_poweroff = ce('on_poweroff')
    at(on_poweroff, 'destroy')
    ac(domain, on_poweroff)

    on_reboot = ce('on_reboot')
    at(on_reboot, 'restart')
    ac(domain, on_reboot)
    
    on_crash = ce('on_crash')
    at(on_crash, 'destroy')
    ac(domain, on_crash)

    memory = ce('memory')
    at(memory, str(mem))
    ac(domain, memory)

    vcpu = ce('vcpu')
    at(vcpu, str(vcpus))
    ac(domain, vcpu)

    devices = getDevicesXML(file, imagetype, mac)
    ac(domain, devices)
    return domain.toxml()

#print getDomainXML('', '', '', '', '', '')

