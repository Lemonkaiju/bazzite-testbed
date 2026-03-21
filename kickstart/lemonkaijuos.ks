# LemonKaijuOS — Installation Kickstart
# Handles locale, partitioning, and bootstrap user creation.
# The ostreecontainer/image deployment directive is injected by
# build-container-installer — do not add one here.

# ── LOCALE & KEYBOARD ────────────────────────────────────────────────────────
lang en_AU.UTF-8
keyboard --vckeymap=us --xlayouts='us'
timezone Australia/Brisbane --utc

# ── NETWORK ──────────────────────────────────────────────────────────────────
network --bootproto=dhcp --device=link --activate --hostname=lemonkaijuos

# ── ACCOUNTS ─────────────────────────────────────────────────────────────────
# Root locked — use sudo via wheel group
rootpw --lock

# Bootstrap admin account used until the first-boot wizard runs.
# The wizard creates permanent family/child accounts and can rename/remove this.
# IMPORTANT: Change this password before production deployment.
user --name=bazzite --groups=wheel --password=BazzVM --plaintext \
     --gecos="LemonKaijuOS Admin"

# ── FIREWALL ─────────────────────────────────────────────────────────────────
# Disabled at install — user configures network security via first-boot wizard
# or STFD integration. Enable manually if deploying without the wizard.
firewall --disabled

# ── SERVICES ─────────────────────────────────────────────────────────────────
services --enabled=NetworkManager

# ── DISK LAYOUT ──────────────────────────────────────────────────────────────
# WARNING: clearpart --all wipes ALL attached disks.
# For machines with multiple drives, replace with:
#   ignoredisk --only-use=nvme0n1   (or sda, vda, etc.)
#   clearpart --all --initlabel --drives=nvme0n1
clearpart --all --initlabel
autopart --type=btrfs

# ── POST-INSTALL ─────────────────────────────────────────────────────────────
%post --erroronfail
# systemd-tmpfiles will create /var/lib/lemonkaijuos on first boot.
# No first-boot-complete flag present = wizard launches on first desktop login.
# Nothing to do here yet — wizard wiring adds to this section in Milestone 3.
%end

# Reboot automatically after install
reboot
