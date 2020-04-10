import takeltest

testinfra_hosts = takeltest.hosts()


def test_takel_anarchism_install_deb_packages_installed(host, testvars):
    install_packages = testvars['takel_gopass_deb_install_packages']

    for install_package in install_packages:
        package = host.package(install_package)

        assert package.is_installed


def test_takel_gopass_install_deb_package_removed(host, testvars):
    deb = testvars['takel_gopass_tmp']

    assert not host.file(deb).exists


def test_takel_anarchism_install_symlink_pass(host):
    gopass = '/usr/local/bin/gopass'
    symlink_pass = host.file('/usr/local/bin/pass')
    assert symlink_pass.linked_to == gopass
