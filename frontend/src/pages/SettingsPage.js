import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Separator } from '../components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Settings, User, Building2, Bell, Shield, Palette, Save, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

export default function SettingsPage() {
  const { user } = useAuth();
  const [saving, setSaving] = useState(false);
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    phone: ''
  });
  const [companyData, setCompanyData] = useState({
    name: '',
    gstin: '',
    pan: '',
    iec_code: '',
    address: '',
    city: '',
    state: ''
  });
  const [notifications, setNotifications] = useState({
    email_payments: true,
    email_shipments: true,
    email_compliance: true,
    whatsapp_payments: false,
    whatsapp_alerts: true
  });

  const handleSaveProfile = async () => {
    setSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success('Profile updated successfully');
    setSaving(false);
  };

  const handleSaveCompany = async () => {
    setSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success('Company details updated');
    setSaving(false);
  };

  const handleSaveNotifications = async () => {
    setSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success('Notification preferences saved');
    setSaving(false);
  };

  return (
    <div className="space-y-6 animate-fade-in" data-testid="settings-page">
      {/* Header */}
      <div>
        <h1 className="font-heading text-4xl text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your account and preferences</p>
      </div>

      {/* Settings Tabs */}
      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="bg-surface border border-border">
          <TabsTrigger value="profile" data-testid="profile-tab">
            <User className="w-4 h-4 mr-2" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="company" data-testid="company-tab">
            <Building2 className="w-4 h-4 mr-2" />
            Company
          </TabsTrigger>
          <TabsTrigger value="notifications" data-testid="notifications-settings-tab">
            <Bell className="w-4 h-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="security" data-testid="security-tab">
            <Shield className="w-4 h-4 mr-2" />
            Security
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <Card className="bg-card border-border" data-testid="profile-settings-card">
            <CardHeader>
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <User className="w-5 h-5 text-primary" />
                Personal Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input
                    id="full_name"
                    value={profileData.full_name}
                    onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                    className="bg-background"
                    data-testid="profile-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profileData.email}
                    onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                    className="bg-background"
                    data-testid="profile-email-input"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  value={profileData.phone}
                  onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                  placeholder="+91 XXXXX XXXXX"
                  className="bg-background"
                  data-testid="profile-phone-input"
                />
              </div>
              <Button onClick={handleSaveProfile} disabled={saving} data-testid="save-profile-btn">
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Changes
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Company Tab */}
        <TabsContent value="company">
          <Card className="bg-card border-border" data-testid="company-settings-card">
            <CardHeader>
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <Building2 className="w-5 h-5 text-primary" />
                Company Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="company_name">Company Name</Label>
                  <Input
                    id="company_name"
                    value={companyData.name}
                    onChange={(e) => setCompanyData({ ...companyData, name: e.target.value })}
                    className="bg-background"
                    data-testid="company-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gstin">GSTIN</Label>
                  <Input
                    id="gstin"
                    value={companyData.gstin}
                    onChange={(e) => setCompanyData({ ...companyData, gstin: e.target.value })}
                    placeholder="22AAAAA0000A1Z5"
                    className="bg-background"
                    data-testid="company-gstin-input"
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="pan">PAN</Label>
                  <Input
                    id="pan"
                    value={companyData.pan}
                    onChange={(e) => setCompanyData({ ...companyData, pan: e.target.value })}
                    placeholder="AAAAA0000A"
                    className="bg-background"
                    data-testid="company-pan-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="iec_code">IEC Code</Label>
                  <Input
                    id="iec_code"
                    value={companyData.iec_code}
                    onChange={(e) => setCompanyData({ ...companyData, iec_code: e.target.value })}
                    placeholder="0123456789"
                    className="bg-background"
                    data-testid="company-iec-input"
                  />
                </div>
              </div>
              <Separator />
              <div className="space-y-2">
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  value={companyData.address}
                  onChange={(e) => setCompanyData({ ...companyData, address: e.target.value })}
                  className="bg-background"
                  data-testid="company-address-input"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={companyData.city}
                    onChange={(e) => setCompanyData({ ...companyData, city: e.target.value })}
                    className="bg-background"
                    data-testid="company-city-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state">State</Label>
                  <Input
                    id="state"
                    value={companyData.state}
                    onChange={(e) => setCompanyData({ ...companyData, state: e.target.value })}
                    className="bg-background"
                    data-testid="company-state-input"
                  />
                </div>
              </div>
              <Button onClick={handleSaveCompany} disabled={saving} data-testid="save-company-btn">
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Company Details
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card className="bg-card border-border" data-testid="notifications-settings-card">
            <CardHeader>
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <Bell className="w-5 h-5 text-primary" />
                Notification Preferences
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-medium mb-4">Email Notifications</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Payment Updates</p>
                      <p className="text-xs text-muted-foreground">Receive emails for payment receipts and reminders</p>
                    </div>
                    <Switch
                      checked={notifications.email_payments}
                      onCheckedChange={(v) => setNotifications({ ...notifications, email_payments: v })}
                      data-testid="email-payments-switch"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Shipment Updates</p>
                      <p className="text-xs text-muted-foreground">Get notified on shipment status changes</p>
                    </div>
                    <Switch
                      checked={notifications.email_shipments}
                      onCheckedChange={(v) => setNotifications({ ...notifications, email_shipments: v })}
                      data-testid="email-shipments-switch"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Compliance Alerts</p>
                      <p className="text-xs text-muted-foreground">LUT renewals, GST deadlines, and more</p>
                    </div>
                    <Switch
                      checked={notifications.email_compliance}
                      onCheckedChange={(v) => setNotifications({ ...notifications, email_compliance: v })}
                      data-testid="email-compliance-switch"
                    />
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="font-medium mb-4">WhatsApp Notifications</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Payment Receipts</p>
                      <p className="text-xs text-muted-foreground">Instant WhatsApp notifications for payments</p>
                    </div>
                    <Switch
                      checked={notifications.whatsapp_payments}
                      onCheckedChange={(v) => setNotifications({ ...notifications, whatsapp_payments: v })}
                      data-testid="whatsapp-payments-switch"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Critical Alerts</p>
                      <p className="text-xs text-muted-foreground">Urgent compliance and risk alerts</p>
                    </div>
                    <Switch
                      checked={notifications.whatsapp_alerts}
                      onCheckedChange={(v) => setNotifications({ ...notifications, whatsapp_alerts: v })}
                      data-testid="whatsapp-alerts-switch"
                    />
                  </div>
                </div>
              </div>
              
              <Button onClick={handleSaveNotifications} disabled={saving} data-testid="save-notifications-btn">
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Preferences
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card className="bg-card border-border" data-testid="security-settings-card">
            <CardHeader>
              <CardTitle className="font-heading text-lg flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Security Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="current_password">Current Password</Label>
                  <Input
                    id="current_password"
                    type="password"
                    placeholder="Enter current password"
                    className="bg-background"
                    data-testid="current-password-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new_password">New Password</Label>
                  <Input
                    id="new_password"
                    type="password"
                    placeholder="Enter new password"
                    className="bg-background"
                    data-testid="new-password-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirm New Password</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    placeholder="Confirm new password"
                    className="bg-background"
                    data-testid="confirm-password-input"
                  />
                </div>
                <Button data-testid="change-password-btn">
                  <Shield className="w-4 h-4 mr-2" />
                  Change Password
                </Button>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="font-medium mb-2">Two-Factor Authentication</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Add an extra layer of security to your account
                </p>
                <Button variant="outline" data-testid="enable-2fa-btn">
                  Enable 2FA
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
