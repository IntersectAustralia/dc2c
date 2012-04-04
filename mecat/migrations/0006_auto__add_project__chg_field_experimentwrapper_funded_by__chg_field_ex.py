# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Project'
        db.create_table('mecat_project', (
            ('experiment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tardis_portal.Experiment'], unique=True, primary_key=True)),
            ('forcode1', self.gf('django.db.models.fields.CharField')(default='060112 Structural Biology', max_length=100, blank=True)),
            ('forcode2', self.gf('django.db.models.fields.CharField')(default='060199 Biochemistry and cell Biology not elsewhere classified', max_length=100, blank=True)),
            ('forcode3', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('funded_by', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('mecat', ['Project'])

        # Changing field 'ExperimentWrapper.funded_by'
        db.alter_column('mecat_experimentwrapper', 'funded_by', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'ExperimentWrapper.forcode2'
        db.alter_column('mecat_experimentwrapper', 'forcode2', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'ExperimentWrapper.forcode3'
        db.alter_column('mecat_experimentwrapper', 'forcode3', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'ExperimentWrapper.forcode1'
        db.alter_column('mecat_experimentwrapper', 'forcode1', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'ExperimentWrapper.notes'
        db.alter_column('mecat_experimentwrapper', 'notes', self.gf('django.db.models.fields.TextField')())


    def backwards(self, orm):
        
        # Deleting model 'Project'
        db.delete_table('mecat_project')

        # Changing field 'ExperimentWrapper.funded_by'
        db.alter_column('mecat_experimentwrapper', 'funded_by', self.gf('django.db.models.fields.TextField')())

        # Changing field 'ExperimentWrapper.forcode2'
        db.alter_column('mecat_experimentwrapper', 'forcode2', self.gf('django.db.models.fields.TextField')())

        # Changing field 'ExperimentWrapper.forcode3'
        db.alter_column('mecat_experimentwrapper', 'forcode3', self.gf('django.db.models.fields.TextField')())

        # Changing field 'ExperimentWrapper.forcode1'
        db.alter_column('mecat_experimentwrapper', 'forcode1', self.gf('django.db.models.fields.TextField')())

        # Changing field 'ExperimentWrapper.notes'
        db.alter_column('mecat_experimentwrapper', 'notes', self.gf('django.db.models.fields.CharField')(max_length=100))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mecat.datasetwrapper': {
            'Meta': {'object_name': 'DatasetWrapper'},
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tardis_portal.Dataset']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mecat.Sample']"})
        },
        'mecat.experimentwrapper': {
            'Meta': {'object_name': 'ExperimentWrapper'},
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tardis_portal.Experiment']"}),
            'forcode1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'forcode2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'forcode3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'funded_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'immutable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'mecat.project': {
            'Meta': {'object_name': 'Project', '_ormbases': ['tardis_portal.Experiment']},
            'experiment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tardis_portal.Experiment']", 'unique': 'True', 'primary_key': 'True'}),
            'forcode1': ('django.db.models.fields.CharField', [], {'default': "'060112 Structural Biology'", 'max_length': '100', 'blank': 'True'}),
            'forcode2': ('django.db.models.fields.CharField', [], {'default': "'060199 Biochemistry and cell Biology not elsewhere classified'", 'max_length': '100', 'blank': 'True'}),
            'forcode3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'funded_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'mecat.sample': {
            'Meta': {'object_name': 'Sample'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tardis_portal.Experiment']"}),
            'forcode1': ('django.db.models.fields.CharField', [], {'default': "'060112 Structural Biology'", 'max_length': '100', 'blank': 'True'}),
            'forcode2': ('django.db.models.fields.CharField', [], {'default': "'060199 Biochemistry and cell Biology not elsewhere classified'", 'max_length': '100', 'blank': 'True'}),
            'forcode3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'immutable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'tardis_portal.dataset': {
            'Meta': {'object_name': 'Dataset'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tardis_portal.Experiment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'immutable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'tardis_portal.experiment': {
            'Meta': {'object_name': 'Experiment'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'handle': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution_name': ('django.db.models.fields.CharField', [], {'default': "'University of Sydney'", 'max_length': '400'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['mecat']
