"""Seed database with initial data"""

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.contract_type import ContractType
from app.models.contract_status import ContractStatus
from app.models.document_type import DocumentType

def seed_database():
    """Populate database with initial data"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Seeding database...")
        
        # Create test user
        print("\n📝 Creating test user...")
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role='user'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            print("   ✅ Test user created: test@example.com / password123")
        else:
            print("   ℹ️  Test user already exists")
        
        # Create contract types
        print("\n📋 Creating contract types...")
        contract_types = [
            {'name': 'service', 'description': 'Service Agreement'},
            {'name': 'nda', 'description': 'Non-Disclosure Agreement'},
            {'name': 'employment', 'description': 'Employment Contract'},
            {'name': 'vendor', 'description': 'Vendor Agreement'},
            {'name': 'lease', 'description': 'Lease Agreement'},
            {'name': 'other', 'description': 'Other'}
        ]
        
        for ct_data in contract_types:
            existing = ContractType.query.filter_by(name=ct_data['name']).first()
            if not existing:
                ct = ContractType(**ct_data)
                db.session.add(ct)
                print(f"   ✅ Created contract type: {ct_data['name']}")
            else:
                print(f"   ℹ️  Contract type exists: {ct_data['name']}")
        
        # Create contract statuses
        print("\n🎯 Creating contract statuses...")
        statuses = [
            {'name': 'draft', 'description': 'Draft - Not yet finalized'},
            {'name': 'pending', 'description': 'Pending Review'},
            {'name': 'active', 'description': 'Active Contract'},
            {'name': 'expired', 'description': 'Expired Contract'},
            {'name': 'renewed', 'description': 'Renewed Contract'}
        ]
        
        for status_data in statuses:
            existing = ContractStatus.query.filter_by(name=status_data['name']).first()
            if not existing:
                status = ContractStatus(**status_data)
                db.session.add(status)
                print(f"   ✅ Created status: {status_data['name']}")
            else:
                print(f"   ℹ️  Status exists: {status_data['name']}")
        
        # Create document types
        print("\n📄 Creating document types...")
        document_types = [
            {'name': 'main_contract', 'description': 'Main Contract Document'},
            {'name': 'supporting', 'description': 'Supporting Document'},
            {'name': 'invoice', 'description': 'Invoice'},
            {'name': 'letter', 'description': 'Letter'},
            {'name': 'amendment', 'description': 'Contract Amendment'},
            {'name': 'other', 'description': 'Other Document'}
        ]
        
        for dt_data in document_types:
            existing = DocumentType.query.filter_by(name=dt_data['name']).first()
            if not existing:
                dt = DocumentType(**dt_data)
                db.session.add(dt)
                print(f"   ✅ Created document type: {dt_data['name']}")
            else:
                print(f"   ℹ️  Document type exists: {dt_data['name']}")
        
        # Commit all changes
        db.session.commit()
        
        print("\n✨ Database seeded successfully!")
        print("\n🔐 Test credentials:")
        print("   Email: test@example.com")
        print("   Password: password123")

if __name__ == '__main__':
    seed_database()
