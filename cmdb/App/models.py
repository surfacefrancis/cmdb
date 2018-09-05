from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#资产共有数据模型
class Asset(models.Model):
    asset_type_choice = (
        ('server','服务器'),
        ('networkdevice','网络设计'),
        ('storagedevice','存储设备'),
        ('securitydevice','安全设备'),
        ('software','软件资产'),
    )

    asset_status = (
        (0,'在线'),
        (1,'下线'),
        (2,'未知'),
        (3,'故障'),
        (4,'备用'),
    )
#verbose_name
# 为字段设置一个人类可读，更加直观的别名。
    asset_type = models.CharField(choices=asset_type_choice,max_length=64,default='server',verbose_name='资产类型')
    name = models.CharField(max_length=64,unique=True,verbose_name='资产名称')
    sn = models.CharField(max_length=128,unique=True,verbose_name='资产序列号')
    business_unit = models.ForeignKey('BusinessUnit',null=True,blank=True,verbose_name='所述业务线')
    status = models.SmallIntegerField(choices=asset_status,default=0,verbose_name='设备状态')
    manufacturer = models.ForeignKey('Manufacturer',null=True,blank=True,verbose_name='制造商')
    manage_ip = models.GenericIPAddressField(null=True,blank=True,verbose_name='管理IP')
    tag = models.ManyToManyField('Tag',blank=True,verbose_name='标签')
    admin = models.ForeignKey(User,null=True,blank=True,verbose_name='资产管理员',related_name='admin')
    idc = models.ForeignKey('IDC',null=True,blank=True,verbose_name='所在机房')
    contract = models.ForeignKey('Contract',null=True,blank=True,verbose_name='合同')
    purchase_day = models.DateField(null=True,blank=True,verbose_name='购买日期')
    expire_day = models.DateField(null=True,blank=True,verbose_name='购买日期')
    price = models.FloatField(null=True,blank=True,verbose_name='价格')
    approved_by = models.ForeignKey(User,null=True,blank=True,verbose_name='批准人',related_name='approved_by')
    memo = models.TextField(null=True,blank=True,verbose_name='备注')
    c_time = models.DateTimeField(auto_now_add=True,verbose_name='批准日期')
    m_time = models.DateTimeField(auto_now=True,verbose_name='更新日期')

    def __str__(self):
        #要获取一个choices的第二元素的值，可以使用get_FOO_display()方法，其中的FOO用字段名代替
        return '<%s>  %s'%(self.get_asset_type_display(),self.name)

    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = '资产总表'
        ordering = ['-c_time']

#服务器模型
class Server(models.Model):
    sub_asset_type_choice = (
        (0,'PC服务器'),
        (1,'刀片机'),
        (2,'小型机')
    )
    create_by_choice = (
        ('auto','自动添加'),
        ('manual','手工录入')
    )
    asset = models.OneToOneField('Asset')
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice,default=0,verbose_name='服务器类型')
    created_by = models.CharField(choices=create_by_choice,max_length=32,default='auto',verbose_name='添加方式')
    hosted_on = models.ForeignKey('self',related_name='hosted_on_server',blank=True,null=True,verbose_name='宿主机')
    model = models.CharField(max_length=128,null=True,blank=True,verbose_name='服务器型号')
    raid_type = models.CharField(max_length=512,blank=True,null=True,verbose_name='Raid类型')
    os_type = models.CharField('操作系统类型',max_length=64,blank=True,null=True)
    os_distribution = models.CharField('发行版本',max_length=64,blank=True,null=True)
    os_release = models.CharField('操作系统版本',max_length=64,blank=True,null=True)

    def __str__(self):
        return '%s--%s--%s <sn:%s>'%(self.asset.name,self.get_sub_asset_type_display(),self.model,self.asset.sn)
    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = '服务器'

#安全、网络、存储设备和软件资产的模型
class SecurityDevice(models.Model):
    sub_asset_type_choice = (
        (0,'防火墙'),
        (1,'入侵检测设备'),
        (2,'互联网网关'),
        (4,'运维审计系统')
    )
    asset = models.OneToOneField('Asset')
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice,default=0,verbose_name='安全设别类型')
    def __str__(self):
        return self.asset.name+'--'+self.get_sub_asset_type_display()+'id:%s'%self.id
    class Meta:
        verbose_name = '安全设备'
        verbose_name_plural = '安全设备'

class StorageDevice(models.Model):
    sub_asset_type_choice = (
        (0,'磁盘阵列'),
        (1,'网络存储器'),
        (2,'磁带库'),
        (4,'磁带机')
    )
    asset = models.OneToOneField('Asset')
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice,default=0,verbose_name='存储设备类型')
    def __str__(self):
        return self.asset.name+'--'+self.get_sub_asset_type_display()+'id:%s'%self.id
    class Meta:
        verbose_name = '存储设备'
        verbose_name_plural = '存储设备'

class NetworkDevice(models.Model):
    sub_asset_type_choice = (
        (0,'路由器'),
        (1,'交换机'),
        (2,'负载均衡'),
        (4,'VPN设备')
    )
    asset = models.OneToOneField('Asset')
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice,default=0,verbose_name='网络设备类型')
    vlan_ip = models.GenericIPAddressField(blank=True,null=True,verbose_name='VLanIP')
    intranet_ip = models.GenericIPAddressField(blank=True,null=True,verbose_name='内网IP')
    model = models.CharField(max_length=128,null=True,blank=True,verbose_name='网络设备型号')
    firmware = models.CharField(max_length=128,blank=True,null=True,verbose_name='设备固件版本')
    port_num = models.SmallIntegerField(null=True,blank=True,verbose_name='端口个数')
    device_detail = models.TextField(null=True,blank=True,verbose_name='详细配置')
    def __str__(self):
        return '%s--%s--%s  <sn:%s>'%(self.asset.name,self.get_sub_asset_type_diplay(),self.model,self.asset.sn)
    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = '网络设备'

class software(models.Model):
    sub_asset_type_choice = (
        (0,'操作系统'),
        (1,'办公\开发软件'),
        (2,'业务软件')
    )
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choice,default=0,verbose_name='软件类型')
    license_num = models.IntegerField(default=1,verbose_name='授权数量')
    version = models.CharField(max_length=64,unique=True,help_text='例如:CentOS release 6.7 (Final)',verbose_name='软件/系统板块')
    def __str__(self):
        return '%s--%s'%(self.get_sub_asset_type_display(),self.version)
    class Meta:
        verbose_name = '软件/系统'
        verbose_name_plural = '系统/软件'

#机房、制造商、业务线、合同、资产标签等数据模型
class IDC(models.Model):
    name = models.CharField(max_length=64,unique=True,verbose_name='机房名称')
    memo = models.CharField(max_length=128,blank=True,null=True,verbose_name='备注')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '机房'
        verbose_name_plural = '机房'
class Manufacturer(models.Model):
    name = models.CharField('厂商名称',max_length=64,null=True)
    telephone = models.CharField('支持电话',max_length=30,blank=True,null=True)
    memo = models.CharField('备注',max_length=128,blank=True,null=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '厂商'
        verbose_name_plural = '厂商'
class BusinessUnit(models.Model):
    parent_unit = models.ForeignKey('self',blank=True,null=True,related_name='parent_level')
    name = models.CharField('业务线',max_length=64,unique=True)
    memo = models.CharField('备注',max_length=64,blank=True,null=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '业务线'
        verbose_name_plural = '业务线'
class Contract(models.Model):
    sn = models.CharField('合同号',max_length=128,unique=True)
    name = models.CharField('合同名称',max_length=64)
    memo = models.TextField('备注',blank=True,null=True)
    price = models.IntegerField('合同金额')
    detail = models.TextField('合同详细',blank=True,null=True)
    start_day = models.DateField('开始日期',blank=True,null=True)
    end_day = models.DateField('失效日期',blank=True,null=True)
    license_num = models.DateField('创建日期',auto_now_add = True)
    c_day = models.DateField('创建日期',auto_add=True)
    m_day = models.DateField('修改日期',auto_nuw = True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '合同'
        verbose_name_plural = '合同'
class Tag(models.Model):
    name = models.CharField('标签名',max_length=32,unique=True)
    c_day = models.DateField('创建日期',auto_now_add=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'

#CPU模型
class CPU(models.Model):
    asset = models.OneToOneField('asset')
    cpu_model = models.CharField('CPU类型',max_length=128,blank=True,null=True)
    cpu_count = models.PositiveSmallIntegerField('物理CPU个数',default=1)
    cpu_core_count = models.PositiveSmallIntegerField('CPU核数',default=1)
    def __str__(self):
        return self.asset.name+':  '+self.cpu_model
    class Meta:
        verbose_name = 'CPU'
        verbose_name_plural = 'CPU'

#RAM模型
class RAM(models.Model):
    asset = models.ForeignKey('Asset')
    sn = models.CharField('SN号',max_length=128,blank=True,null=True)
    model = models.CharField('内存型号',max_length=128,blank=True,null=True)
    manufacturer = models.CharField('内存制造商',max_length=128,blank=True,null=True)
    slot = models.CharField('插槽',max_length=64)
    capacity = models.IntegerField('内存大小（GB）',blank=True,null=True)
    def __str__(self):
        return '%s: %s: %s: %s'%(self.asset.name,self.model,self.slot,self.capacity)
    class Meta:
        verbose_name = '内存'
        verbose_name_plural = '内存'
        unique_together = ('asset','slot')

#硬盘模型
class Disk(models.Model):
    disk_interface_type_chioce = (
        ('SATA','SATA'),
        ('SAS','SAS'),
        ('SCSI','SCSI'),
        ('SSD','SSD'),
        ('unknown','unknown')
    )
    asset = models.ForeignKey('Asset')
    sn = models.CharField('硬盘SN号',max_length=128)
    slot = models.CharField('所在插槽位',max_length=64,blank=True,null=True)
    model = models.CharField('磁盘型号',max_length=128,blank=True,null=True)
    manufacturer = models.CharField('磁盘制造商',max_length=128,blank=True,null=True)
    capacity = models.FloatField('磁盘容量(GB)',blank=True,null=True)
    interface_ytpe = models.CharField('接口类型',max_length=16,choices=disk_interface_type_chioce,default='unknown')
    def __str__(self):
        return '%s: %s: %s: %sGB'%(self.asset.name,self.model,self.slot,self.capacity)
    class Meta:
        verbose_name = '硬盘'
        verbose_name_plural = '硬盘'
        unique_together = ('asset','sn')

#网卡模型
class NIC(models.Model):
    asset = models.ForeignKey('Asset')
    name = models.CharField('网卡名称',max_length=64,blank=True,null=True)
    model = models.CharField('网卡型号',max_length=128)
    mac = models.CharField('MAC地址',max_length=64)
    ip_address = models.GenericIPAddressField('IP地址',blank=True,null=True)
    net_mask = models.CharField('掩码',max_length=64,blank=True,null=True)
    bonding = models.CharField('绑定地址',max_length=64,blank=True,null=True)
    def __str__(self):
        return '%s: %s: %s'%(self.asset.name,self.model,self.mac)
    class Meta:
        verbose_name = '网卡'
        verbose_name_plural = '网卡'
        unique_together = ('asset','model','mac')

#日志模型
class EventLog(models.Model):
    name = models.CharField('事件名称',max_length=128)
    event_type_choice = (
        (0,'其他'),
        (1,'硬件变更'),
        (2,'新增配件'),
        (3,'设备下线'),
        (4,'设备上线'),
        (5,'定期维护'),
        (6,'业务上线\更新\变更'),
    )
    asset = models.ForeignKey('Asset',blank=True,null=True,on_delete=models.SET_NULL)
    new_asset = models.ForeignKey('NewAssetApprovalZone',blank=True,null=True,on_delete=models.SET_NULL)
    event_type = models.SmallIntegerField('事件类型',choices=event_type_choice,default=4)
    component = models.CharField('时间子项',max_length=256,blank=True,null=True)
    detail = models.TextField('时间详情')
    data = models.DateTimeField('事件时间',auto_now_add=True)
    user = models.ForeignKey(User,blank=True,null=True,verbose_name='事件执行人',on_delete=models.SET_NULL)
    memo = models.TextField('备注',blank=True,null=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '事件记录'
        verbose_name_plural = '事件记录'

#新资产待审批区模型
class NewAssetApprovalZone(models.Model):
    sn = models.CharField('资产SN号',max_length=128,unique=True)
    asset_type_choice = (
        ('server','服务器'),
        ('networkdevice','网络设备'),
        ('storagedevice','存储设备'),
        ('securitydevice','安全设备'),
        ('IDC','机房'),
        ('software','软甲资产')
    )
    asset_type = models.CharField(choices=asset_type_choice,default='server',max_length=64,blank=True,null=True,verbose_name='资产类型')
    manufacturer = models.CharField(max_length=64,blank=True,null=True,verbose_name='生产厂商')
    ram_size = models.PositiveIntegerField(blank=True,null=True,verbose_name='内存大小')
    model = models.CharField(max_length=128,blank=True,null=True,verbose_name='型号')
    cpu_model = models.CharField(max_length=128,blank=True,null=True)
    cpu_count = models.PositiveSmallIntegerField(blank=True,null=True)
    cpu_core_count = models.PositiveSmallIntegerField(blank=True,null=True)
    os_distribution = models.CharField(max_length=64,blank=True,null=True)
    os_release = models.CharField(max_length=64,blank=True,null=True)
    os_type = models.CharField(max_length=64,blank=True,null=True)
    data = models.TextField('资产数据')
    c_time = models.DateTimeField('汇报日期',auto_now_add=True)
    m_time = models.DateTimeField('数据更新日期',auto_now=True)
    approved = models.BooleanField('是否批准',default=False)
    def __str__(self):
        return self.sn
    class Meta:
        verbose_name = '新上线待批准资产'
        verbose_name_plural = '新上线待批准资产'
        ordering = ['-c_time']






































