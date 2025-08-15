'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { 
  ChevronRight, 
  ChevronDown, 
  Search, 
  Package, 
  Settings, 
  Layers, 
  FolderOpen,
  Folder,
  ExternalLink,
  RotateCw as Sync  // Use RotateCw instead of Sync
} from 'lucide-react';
import { oidSystemService } from '@/lib/oid-integration';

interface OIDNode {
  id: string;
  name: string;
  type: 'product' | 'service' | 'solution' | 'category';
  parent_id?: string;
  children?: OIDNode[];
  metadata: {
    description: string;
    price?: number;
    currency?: string;
    features?: string[];
    technologies?: string[];
    target_market?: string;
    complexity_level?: 'basic' | 'advanced' | 'enterprise';
  };
  relationships: {
    dependencies?: string[];
    integrates_with?: string[];
    extends?: string[];
  };
  status: 'active' | 'deprecated' | 'coming_soon';
  created_at: string;
  updated_at: string;
}

interface TreeNodeProps {
  node: OIDNode;
  level: number;
  expandedNodes: Set<string>;
  onToggle: (_nodeId: string) => void;
  onSelect: (_node: OIDNode) => void;
  selectedNode?: OIDNode;
}

function TreeNode({ node, level, expandedNodes, onToggle, onSelect, selectedNode }: TreeNodeProps) {
  const isExpanded = expandedNodes.has(node.id);
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selectedNode?.id === node.id;

  const getIcon = () => {
    switch (node.type) {
      case 'product': return <Package className="h-4 w-4" />;
      case 'service': return <Settings className="h-4 w-4" />;
      case 'solution': return <Layers className="h-4 w-4" />;
      case 'category': return hasChildren ? (isExpanded ? <FolderOpen className="h-4 w-4" /> : <Folder className="h-4 w-4" />) : <Folder className="h-4 w-4" />;
      default: return <Package className="h-4 w-4" />;
    }
  };

  const getStatusColor = () => {
    switch (node.status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'deprecated': return 'bg-red-100 text-red-800';
      case 'coming_soon': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="select-none">
      <div
        className={`flex items-center py-2 px-2 rounded-md cursor-pointer hover:bg-gray-50 ${
          isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : ''
        }`}
        style={{ paddingLeft: `${level * 20 + 8}px` }}
        onClick={() => onSelect(node)}
      >
        {hasChildren && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggle(node.id);
            }}
            className="mr-2 p-1 hover:bg-gray-200 rounded"
          >
            {isExpanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          </button>
        )}
        
        <div className="mr-2">{getIcon()}</div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium truncate">{node.name}</span>
            <Badge variant="outline" className={`text-xs ${getStatusColor()}`}>
              {node.status}
            </Badge>
            {node.metadata.price && (
              <Badge variant="secondary" className="text-xs">
                ${node.metadata.price.toLocaleString()}
              </Badge>
            )}
          </div>
          {node.metadata.description && (
            <p className="text-xs text-gray-500 truncate mt-1">
              {node.metadata.description}
            </p>
          )}
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div>
          {node.children!.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              level={level + 1}
              expandedNodes={expandedNodes}
              onToggle={onToggle}
              onSelect={onSelect}
              selectedNode={selectedNode}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function OIDTreeViewer() {
  const [nodes, setNodes] = useState<OIDNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNode, setSelectedNode] = useState<OIDNode | undefined>();
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [filteredNodes, setFilteredNodes] = useState<OIDNode[]>([]);
  const [lastSync, setLastSync] = useState<string>('');

  const filterNodes = useCallback(() => {
    if (!searchTerm.trim()) {
      setFilteredNodes(nodes);
      return;
    }

    const filtered = nodes.filter(node =>
      node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.metadata.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.metadata.technologies?.some(tech => 
        tech.toLowerCase().includes(searchTerm.toLowerCase())
      )
    );

    setFilteredNodes(filtered);
  }, [nodes, searchTerm]);

  useEffect(() => {
    loadOIDTree();
    checkLastSync();
  }, []);

  useEffect(() => {
    filterNodes();
  }, [filterNodes]);

  const loadOIDTree = async () => {
    setLoading(true);
    try {
      // Try to load from OID system first, fallback to synced data
      let oidNodes: OIDNode[] = [];
      
      try {
        oidNodes = await oidSystemService.getOIDTree({ include_children: true });
      } catch (error) {
        // OID system unavailable, using fallback data
        // Use fallback B2B solutions as OID nodes
        const b2bSolutions = await oidSystemService.getB2BSolutions();
        oidNodes = b2bSolutions.map(solution => ({
          id: solution.id,
          name: solution.name,
          type: 'solution' as const,
          metadata: {
            description: solution.description,
            price: solution.price,
            currency: solution.currency,
            features: solution.features,
            technologies: solution.technologies,
            target_market: solution.target_market,
            complexity_level: solution.complexity_level,
          },
          relationships: {
            dependencies: [],
            integrates_with: [],
            extends: [],
          },
          status: solution.status as 'active',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }));
      }

      setNodes(oidNodes);
      
      // Auto-expand root nodes
      const rootNodes = oidNodes.filter(node => !node.parent_id);
      setExpandedNodes(new Set(rootNodes.map(node => node.id)));
      
    } catch (error) {
      // Failed to load OID tree
    } finally {
      setLoading(false);
    }
  };

  const checkLastSync = () => {
    if (typeof window !== 'undefined') {
      const lastSyncTime = localStorage.getItem('oid_last_sync');
      if (lastSyncTime) {
        setLastSync(new Date(lastSyncTime).toLocaleString());
      }
    }
  };

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const syncWithOID = async () => {
    setLoading(true);
    try {
      await oidSystemService.syncWithStore();
      await loadOIDTree();
      checkLastSync();
    } catch (error) {
      // Failed to sync with OID system
    } finally {
      setLoading(false);
    }
  };

  const openInOIDPortal = () => {
    if (selectedNode) {
      // This would open the OID portal with the selected node
      const oidPortalUrl = `https://oid.brainsait.io/portal/nodes/${selectedNode.id}`;
      window.open(oidPortalUrl, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">BrainSAIT OID System</h2>
          <p className="text-muted-foreground">
            Explore the unified platform object identification system
          </p>
          {lastSync && (
            <p className="text-xs text-muted-foreground mt-1">
              Last synced: {lastSync}
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={syncWithOID} disabled={loading}>
            <Sync className="w-4 h-4 mr-2" />
            Sync
          </Button>
          {selectedNode && (
            <Button variant="outline" onClick={openInOIDPortal}>
              <ExternalLink className="w-4 h-4 mr-2" />
              Open in OID Portal
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tree View */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>OID Tree Structure</CardTitle>
              <CardDescription>
                Navigate through the BrainSAIT ecosystem components
              </CardDescription>
              
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search OID nodes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="max-h-96 overflow-y-auto">
                {filteredNodes.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    {searchTerm ? 'No matching nodes found' : 'No OID nodes available'}
                  </div>
                ) : (
                  <div className="space-y-1">
                    {filteredNodes.map((node) => (
                      <TreeNode
                        key={node.id}
                        node={node}
                        level={0}
                        expandedNodes={expandedNodes}
                        onToggle={toggleNode}
                        onSelect={setSelectedNode}
                        selectedNode={selectedNode}
                      />
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detail View */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Node Details</CardTitle>
            </CardHeader>
            
            <CardContent>
              {selectedNode ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg">{selectedNode.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {selectedNode.metadata.description}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Type:</span>
                      <p className="capitalize">{selectedNode.type}</p>
                    </div>
                    <div>
                      <span className="font-medium">Status:</span>
                      <p className="capitalize">{selectedNode.status}</p>
                    </div>
                  </div>

                  {selectedNode.metadata.price && (
                    <div>
                      <span className="font-medium">Price:</span>
                      <p className="text-lg font-bold">
                        ${selectedNode.metadata.price.toLocaleString()} {selectedNode.metadata.currency}
                      </p>
                    </div>
                  )}

                  {selectedNode.metadata.target_market && (
                    <div>
                      <span className="font-medium">Target Market:</span>
                      <p>{selectedNode.metadata.target_market}</p>
                    </div>
                  )}

                  {selectedNode.metadata.complexity_level && (
                    <div>
                      <span className="font-medium">Complexity:</span>
                      <Badge className="ml-2">
                        {selectedNode.metadata.complexity_level}
                      </Badge>
                    </div>
                  )}

                  {selectedNode.metadata.features && selectedNode.metadata.features.length > 0 && (
                    <div>
                      <span className="font-medium">Features:</span>
                      <ul className="list-disc list-inside mt-2 space-y-1">
                        {selectedNode.metadata.features.map((feature, index) => (
                          <li key={index} className="text-sm">{feature}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {selectedNode.metadata.technologies && selectedNode.metadata.technologies.length > 0 && (
                    <div>
                      <span className="font-medium">Technologies:</span>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {selectedNode.metadata.technologies.map((tech, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Relationships */}
                  {(selectedNode.relationships.dependencies?.length || 
                    selectedNode.relationships.integrates_with?.length || 
                    selectedNode.relationships.extends?.length) && (
                    <div>
                      <span className="font-medium">Relationships:</span>
                      <div className="mt-2 space-y-2">
                        {(selectedNode.relationships?.dependencies?.length ?? 0) > 0 && (
                          <div>
                            <p className="text-xs font-medium text-muted-foreground">Dependencies:</p>
                            <div className="flex flex-wrap gap-1">
                              {selectedNode.relationships?.dependencies?.map((dep, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {dep}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {(selectedNode.relationships?.integrates_with?.length ?? 0) > 0 && (
                          <div>
                            <p className="text-xs font-medium text-muted-foreground">Integrates with:</p>
                            <div className="flex flex-wrap gap-1">
                              {selectedNode.relationships?.integrates_with?.map((integration, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {integration}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="pt-4 border-t">
                    <div className="text-xs text-muted-foreground">
                      <p>Created: {new Date(selectedNode.created_at).toLocaleDateString()}</p>
                      <p>Updated: {new Date(selectedNode.updated_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Select a node to view details
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}