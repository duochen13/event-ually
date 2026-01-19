from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, Conversation, Message, DataSource, Context
from commands.command_parser import is_command, route_command
from browsing_stats import get_daily_stats, get_weekly_summary
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    os.environ.get("FRONTEND_URL", "")
]
allowed_origins = [origin for origin in allowed_origins if origin]

CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# ==================== CONVERSATION ROUTES ====================

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    conversations = Conversation.query.order_by(Conversation.updated_at.desc()).all()
    return jsonify([conv.to_dict() for conv in conversations]), 200

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    data = request.get_json() or {}
    title = data.get('title', f'Conversation {datetime.now().strftime("%Y-%m-%d %H:%M")}')

    conversation = Conversation(title=title)
    db.session.add(conversation)
    db.session.commit()

    return jsonify(conversation.to_dict()), 201

@app.route('/api/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation with its messages"""
    conversation = Conversation.query.get_or_404(conversation_id)
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()

    return jsonify({
        'conversation': conversation.to_dict(),
        'messages': [msg.to_dict() for msg in messages]
    }), 200

@app.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation and all its messages"""
    conversation = Conversation.query.get_or_404(conversation_id)
    db.session.delete(conversation)
    db.session.commit()

    return jsonify({'message': 'Conversation deleted successfully'}), 200

@app.route('/api/conversations/<int:conversation_id>/title', methods=['PUT'])
def update_conversation_title(conversation_id):
    """Update conversation title"""
    conversation = Conversation.query.get_or_404(conversation_id)
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    conversation.title = data['title']
    db.session.commit()

    return jsonify(conversation.to_dict()), 200

# ==================== MESSAGE ROUTES ====================

@app.route('/api/conversations/<int:conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Send a message and get AI response"""
    conversation = Conversation.query.get_or_404(conversation_id)
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({'error': 'Message content is required'}), 400

    # Create user message
    user_message = Message(
        conversation_id=conversation_id,
        role='user',
        content=data['content'],
        meta_data=json.dumps(data.get('metadata', {}))
    )
    db.session.add(user_message)

    # Check if message is a command
    content = data['content']
    if is_command(content):
        # Route to command handler
        ai_response_content = route_command(content, conversation_id)
    else:
        # Get normal AI response
        ai_response_content = get_ai_response(conversation_id, content)

    # Create assistant message
    assistant_message = Message(
        conversation_id=conversation_id,
        role='assistant',
        content=ai_response_content,
        meta_data=json.dumps({'model': 'claude-sonnet-4-5'})
    )
    db.session.add(assistant_message)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'user_message': user_message.to_dict(),
        'assistant_message': assistant_message.to_dict()
    }), 201

def get_ai_response(conversation_id, user_message):
    """
    Get AI response using Claude API
    This is a placeholder implementation. In production, you would:
    1. Fetch conversation history
    2. Gather context from enabled data sources
    3. Call Claude API with proper prompt engineering
    4. Return the AI response
    """
    # Check if Claude API key is configured
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        return "⚠️ AI Assistant not configured. Please set ANTHROPIC_API_KEY environment variable to enable AI responses. For now, I'm a placeholder response!"

    try:
        # Import anthropic SDK
        import anthropic

        # Get conversation history
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()

        # Build message history for Claude API
        claude_messages = []
        for msg in messages:
            claude_messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add current user message
        claude_messages.append({
            "role": "user",
            "content": user_message
        })

        # Get enabled data sources context
        data_sources = DataSource.query.filter_by(enabled=True).all()
        context_info = []
        for ds in data_sources:
            contexts = Context.query.filter_by(data_source_id=ds.id).order_by(Context.created_at.desc()).limit(5).all()
            if contexts:
                context_info.append(f"\n--- {ds.name} Data ---")
                for ctx in contexts:
                    context_info.append(ctx.summary or ctx.content[:200])

        # Build system prompt with context
        system_prompt = f"""You are a highly customized AI assistant built for a senior software engineer at Meta.
You have access to various data sources and can provide contextual, intelligent responses.

Available data sources: {', '.join([ds.name for ds in data_sources])}

{chr(10).join(context_info) if context_info else 'No additional context available.'}

Provide helpful, accurate, and context-aware responses."""

        # Call Claude API
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            system=system_prompt,
            messages=claude_messages
        )

        return response.content[0].text

    except ImportError:
        return "⚠️ Anthropic SDK not installed. Run: pip install anthropic"
    except Exception as e:
        return f"⚠️ Error getting AI response: {str(e)}"

# ==================== DATA SOURCE ROUTES ====================

@app.route('/api/data-sources', methods=['GET'])
def get_data_sources():
    """Get all data sources"""
    data_sources = DataSource.query.order_by(DataSource.name).all()
    return jsonify([ds.to_dict() for ds in data_sources]), 200

@app.route('/api/data-sources', methods=['POST'])
def create_data_source():
    """Create a new data source"""
    data = request.get_json()

    if not data or 'name' not in data or 'type' not in data:
        return jsonify({'error': 'Name and type are required'}), 400

    data_source = DataSource(
        name=data['name'],
        type=data['type'],
        enabled=data.get('enabled', True),
        config=json.dumps(data.get('config', {}))
    )

    db.session.add(data_source)
    db.session.commit()

    return jsonify(data_source.to_dict()), 201

@app.route('/api/data-sources/<int:data_source_id>', methods=['PUT'])
def update_data_source(data_source_id):
    """Update a data source"""
    data_source = DataSource.query.get_or_404(data_source_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in data:
        data_source.name = data['name']
    if 'type' in data:
        data_source.type = data['type']
    if 'enabled' in data:
        data_source.enabled = data['enabled']
    if 'config' in data:
        data_source.config = json.dumps(data['config'])

    db.session.commit()

    return jsonify(data_source.to_dict()), 200

@app.route('/api/data-sources/<int:data_source_id>', methods=['DELETE'])
def delete_data_source(data_source_id):
    """Delete a data source"""
    data_source = DataSource.query.get_or_404(data_source_id)
    db.session.delete(data_source)
    db.session.commit()

    return jsonify({'message': 'Data source deleted successfully'}), 200

# ==================== CONTEXT ROUTES ====================

@app.route('/api/data-sources/<int:data_source_id>/contexts', methods=['POST'])
def add_context(data_source_id):
    """Add context to a data source"""
    data_source = DataSource.query.get_or_404(data_source_id)
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400

    context = Context(
        data_source_id=data_source_id,
        content=data['content'],
        summary=data.get('summary')
    )

    db.session.add(context)
    db.session.commit()

    return jsonify(context.to_dict()), 201

# ==================== BROWSING HISTORY STATS ====================

@app.route('/api/browsing-history/daily', methods=['GET'])
def get_daily_browsing_stats():
    """Get daily browsing statistics for the last N days"""
    try:
        days = request.args.get('days', default=7, type=int)
        days = min(days, 30)  # Cap at 30 days max

        stats = get_daily_stats(days=days)
        return jsonify({'daily_stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/browsing-history/weekly', methods=['GET'])
def get_weekly_browsing_stats():
    """Get weekly browsing summary"""
    try:
        summary = get_weekly_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Assistant Backend is running',
        'anthropic_configured': bool(os.environ.get('ANTHROPIC_API_KEY'))
    }), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
