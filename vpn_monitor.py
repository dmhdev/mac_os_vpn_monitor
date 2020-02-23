import subprocess, time

class VPNMonitor:

    def __init__(self, vpn_connection_name, app_name, vpn_check_interval):
        self.vpn_connection_name = vpn_connection_name
        self.app_name = app_name
        self.vpn_check_interval = vpn_check_interval
        
 
    def monitor_vpn(self):
        """
        Start VPN if inactive, and close App if VPN disconnects
        """

        vpn_check_count = 0
        connection_failures = 0

        while (connection_failures < 5):

            # Check network processes for VPN
            if self.vpn_active(): # @todo: also check if app is running
                # VPN is running
                if vpn_check_count % 10 == 0:
                    print('%s VPN Running...' % self.vpn_name)
                vpn_check_count += 1

            else:
                # VPN disconnected, kill app
                self.kill_app()

                # Try to reconnect VPN
                if self.reconnect_vpn():
                    self.restart_app()
                else:
                    connection_failures += 1
                # @todo: check if app is restarted successfully

            time.sleep(self.vpn_check_interval)


    def vpn_active(self):
        """
        Check if VPN is currently running
        """
        proc_check = subprocess.run(["scutil --nc list | grep Connected"],shell=True, stdout=subprocess.PIPE)
        if (self.vpn_connection_name in str(proc_check.stdout) and 'Connected' in str(proc_check.stdout)):
            return True
        return False

    def kill_app(self):
        """
        Kills selected App
        """
        print( '---\n%s VPN Disconnected! Closing %s...' % (self.vpn_connection_name, self.app_name) )
        subprocess.run([" osascript -e 'quit app \"%s\"' " % self.app_name],shell=True)
        print('%s Closed!\n---' % self.app_name)

    def restart_app(self):
        """
        Try to restart App
        """
        print('Restarting App %s...' % self.app_name)
        subprocess.run([ "open -a %s" % self.app_name],shell=True)
        print('%s Restarted!\n---' % self.app_name)
        
    def reconnect_vpn(self):
        """
        Try to reconnect VPN 10 times
        """
        for reconnect_try in range(1,11):
            print('Attempt %d to reconnect VPN...' % reconnect_try)
            subprocess.run([ "networksetup -connectpppoeservice \"%s\" " % self.vpn_connection_name],shell=True)
            time.sleep(10)
            if self.vpn_active():
                print('%s VPN Restarted...\n---' % self.vpn_connection_name)
                return True
        return False
        
        
if __name__ == "__main__":
    vpn_connection_name = 'VPN Connection Name'
    app_name = 'App Name'
    vpn_check_interval = 10
    
    vpn_monitor = VPNMonitor(vpn_connection_name, app_name, vpn_check_interval)
    vpn_monitor.monitor_vpn()
